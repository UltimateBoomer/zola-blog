+++
title = "Tuning Strata: ~60 TPS of Qwen3.8-Flash-Next on an RX 7800 XT"
description = "Optimizing performance of local LLM hosting"
date = "2026-10-15"
[taxonomies]
categories = ["Write-up"]
tags = ["Strata", "Llama.cpp", "Optimization"]
+++

Local LLMs have come a long way in a short amount of time.
Since last year, if you just look at models that can feasibly run on a 16 GB GPU, we went from Llama-3.1 8B, Qwen-2.5 32B, Mistral Small 24B, etc., which can barely make coherent tool calls, to Qwen3.8-27B and Qwen3.8-Flash-Next (FN), which can do some relatively complex tasks like implementing features and reasoning through difficult math problems.
Of course, part of this evolution comes from improvements in the harness (e.g. Pi agent), but we should not discount the evolution in LLM inference tools, notably llama.cpp.

Recently I discovered the latest leap in local LLM inference, [Strata](https://github.com/Niko1221/Strata).
It is a llama.cpp-based engine that targets MoE models, specifically [Qwen3.8-Flash-Next](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF).
The main innovation comes from being able to distribute individual experts on both the GPU and the CPU, rather than placing entire expert layers on either the GPU or CPU.
This makes it so each token inference that hits an expert on the GPU is fully accelerated, rather than having to go through both GPU and CPU layers.
This leads to a 2-3x improvement over llama.cpp in the case where the whole model cannot fit in VRAM, which is certainly the case with the FN model.

## Baseline: Qwen3.8-27B on llama.cpp

My hardware consists of a Ryzen 7 7800X3D, 32 GB SK Hynix DDR5-6000 RAM, and a Radeon RX 7800 XT (16 GB).
I tuned the memory slightly, with stability tested in y-cruncher.
I left my GPU alone as it seems even small changes to VRAM speed led to issues.
For my OS, I'm using the latest Fedora 44 with mostly out of the box settings, other than using a 32 GB swap file on disk with zswap rather than the default zram setup.
And I use the Pi agent 1.2.0 as the harness.

My previous setup hosted the dense model Qwen3.8-27B using Podman Compose with a llama.cpp Vulkan image.
Compose makes it easy to pin a specific container image and track the resources used by the deployment.
On my setup, I experimented with Unsloth's Dynamic v3 quants of Qwen3.8-27B: `UD-Q3_K_XL`, `UD-Q4_K_XL`, and `UD-Q6_K_XL` - the largest quant in each of the 3-, 4-, and 6-bit groups - with 3-token MTP, a 60K context window, `q8_0` KV cache, every layer offloaded to the GPU for computation, and Unsloth's recommended inference settings.
My goal is to use the model as a teacher for my coursework involving some pure math, computing theory and cryptography.
With my typical workload of reading through course notes and answering a question, here is a table of the results.

| model | prefill (tps) | decode (tps) |
|---|---|---|
| Qwen3.8-27B `UD-Q3_K_XL` | 500 | 32 |
| Qwen3.8-27B `UD-Q4_K_XL` | 380 | 15 |
| Qwen3.8-27B `UD-Q6_K_XL` | 260 | 11 |

At Q4 and above, the weights plus the KV cache exceed my 16 GB of VRAM, so part of the model has to live in host memory while the math still runs on the GPU.
This is where the Vulkan build comes in.
On ROCm/HIP, a buffer is allocated either entirely in VRAM or entirely in system RAM (unified memory); as far as I know, there is no way to split one allocation between the two.
Vulkan does this in userspace, so the model can take up more memory than the card actually has while still being computed on the GPU.
It does require tuning: past a certain point, streaming a layer's weights over PCIe is slower than just running that layer on the CPU.

Overall, I think Qwen3.8-27B is a great model, able to achieve solid results for what I want it to do.
The exact quality of the model can be found in benchmarks anywhere online; in my experience, the higher quantizations are indeed more stable, at the cost of a linear drop in inference speed.
Without the expectation of an immediate real-time response, the model felt pretty alright to use, and considerably better than the models of a year ago.
It was able to come to the right answer in the vast majority of cases, and deliver the result in a structured manner, though not very concise unlike some of the new frontier models.
Comparing the quants, the 3-bit run was faster on the more straightforward questions, while the higher-bit ones were more stable for longer sessions.
And surprisingly, the models rarely looped even at `UD-Q3_K_XL`, which is great and shows that quantization has come far as well.

## Strata: Qwen3.8-Flash-Next

After Strata became popular, I tested it on my setup to see if it could replace my Qwen3.8-27B llama.cpp deployment.
I used the ROCm/HIP version this time.
Being a MoE model, out of 125B parameters (and 51B ngram parameters streamable from disk), FN has only 6B active parameters, which should let it run very fast provided most weights fit in memory.
I chose the `q2_0` model as it is the largest one that fits without heavy swapping.

At first, I used the default configuration, with a 100K context window (it seems to fit at least that much on the GPU) and Qwen's recommended sampling parameters.
I got around 40 TPS on decode with these settings, occasionally dropping down to 10 TPS.
So the model already has very good performance compared to the dense model, but is inconsistent at times.
The biggest issue is that it often encounters deadlocks, during which prefill or decode speeds drop significantly, often causing Strata to restart the model.
This is an [actual issue](https://github.com/Niko1221/Strata/issues/2065) upstream, likely induced when there is heavy swapping.

In my initial tests, compared to the dense model, FN appears to have a greater breadth in knowledge.
Which makes sense, after all, it has more parameters.
This actually makes it more ideal for my workload, where knowledge in mathematics is more important compared to typical SWE tasks.

Seeing the results, I ran Strata's calibration feature, which pointed to a few config changes, most notably the PCIe fraction and the prefill batch size.
The PCIe fraction lets some experts sit in RAM while still being read by the GPU.
This is especially important on a single-CCD Ryzen setup such as mine, where the CPU cannot access the full memory bandwidth.
The default 8192 prefill batch size was too heavy, often causing GPU-side stalls and deadlocks, which are still open issues on Strata.

After some tuning, I get this result consistently:

| model | prefill (tps) | decode (tps) |
|---|---|---|
| Qwen3.8-Flash-Next `q2_0` | ~500 | 52-62 |

The reduced prefill batch size alleviated the deadlocking issue, and additional tuning gave a decent increase to decode speed while making it a stay at the speed consistently.

### Qwen3.8-Flash-Next on llama.cpp

With Strata's popularity, some improvements to running MoE models in llama.cpp have also been merged.
So I tested the current state of llama.cpp as well, with the exact same model.
However, llama.cpp cannot yet replicate Strata's expert splitting, so it has to place entire expert layers on either the CPU or the GPU, which slows inference considerably.
Once the main Strata improvements are upstreamed to llama.cpp, I'll test it again.

## How I set it up

While Strata has its own recommended install steps, because I care about application and infrastructure security, I set Strata up with Podman Compose in a self-contained environment.

To do this, I followed this [discussion](https://github.com/podman-container-tools/podman/discussions/28320), created an unprivileged user on the host with Podman socket enabled to allow remote Podman connection over SSH, where I can manage Podman through a remote VM.
Then, I created a compose file with an init container downloading the model from HuggingFace, followed by Strata itself in a custom ROCm Ubuntu image.
This setup containerizes the Strata application with minimal overhead, and prepares it to be incorporated into my self-hosted cluster.

The exact setup is available in [this repo](https://github.com/UltimateBoomer/strata-local).

### Conversation cache

While testing various ways to improve performance, I implemented an additional feature for Strata: a *disk-based conversation cache*.
Upstream Strata can cache conversations only in RAM, but we are prett already fully utilizing all the memory available for the experts.
My fork adds an option to move the cache to the disk: when the engine switches away from a conversation, it writes that conversation's K/V image to a snapshot on disk.
When a later request continues that session, the engine streams the snapshot back instead of re-prefilling the whole prompt.
A 22K-token prompt that would take about 47 s to process again now responds in 1 s, so alternating turns between several sessions costs a second rather than a minute.

In practice, this makes concurrent sessions more usable.
For example, it allows subagents to be used more effectively, as well as handling multiple conversations in parallel.
The only tradeoff is that data is written disk rather than RAM: a snapshot is about 0.7 GB per 22K tokens, up to roughly 2.5 GB at full context.
This could potentially induce a lot of writes on your SSD, but it all depends on your workload.

My fork is available [here](https://github.com/UltimateBoomer/Strata).

## Conclusion

From my testing, Strata achieves great performance for Qwen3.8-Flash-Next at `q2_0` on my setup, which is essentially a common 2024 PC build.
Compared to modern Anthropic and OpenAI models, I think it is around the level of Claude Haiku 4.5 or GPT-5.6 Luna.
Do note that at `q2_0` level there is likely going to be a significant loss in quality compared to the full model, but for what it can achieve on the limited hardware, it is very impressive.
And certainly good enough to do some actual work such as clearly scoped implementation and mathematical problem solving.
With some tuning and additional setup-specific improvements, the model becomes surprisingly usable, and responds faster than a cloud model during peak hours.

As of mid-October 2026, I think we are at the point where local LLMs are starting to become a serious option for those with decent consumer hardware, especially if you have hardware bought right before the whole GPU and RAM price escalation of 2025-2026.
So if you are interested in using AI and have capable hardware, give local LLMs a try!
Even though buying new hardware for LLM hosting might not be worth it compared to getting a subscription (unfortunately this is partially caused by the improvements in local LLMs), it is still a good learning opportunity on the topic of infra and homelabbing, not to mention the tangible privacy and availability benefits.
If cloud providers ever raise their prices or becomes unavailable for whatever reason, you can take comfort in knowing you always have a good model to fall back on.

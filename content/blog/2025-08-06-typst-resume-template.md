+++
title = "A Simple Typst Resume"
description = "How I rewrote my LaTeX resume in Typst"
date = "2025-08-06"
[taxonomies]
categories = ["Write-up"]
tags = ["Typst", "Resume"]
+++

## Introduction
If you've ever used LaTeX to write a resume, especially from one of the [commonly used templates](https://www.overleaf.com/latex/templates/tagged/cv), you've probably felt the following issues.

### Packages
First, why is there a massive 50-line header at the beginning of the document?
And why do we need to include so many packages just for some basic formatting functionality like font and text size?
While there is plenty of documentation for every single package, it's still a lot of effort to find out what each package does and how to use it.
It's also quite unintuitive when you want to change the layout and formatting of the page, even if you're familiar with LaTeX basics.

### Verboseness and lack of modularity
Second, take a look at what a typical resume block looks like in LaTeX (source: [RenderCV EngineeringResumes Theme](https://www.overleaf.com/latex/templates/rendercv-engineeringresumes-theme/shwqvsxdgkjy)):
```latex
\begin{twocolentry}{June 2005 – Aug 2007}
  \textbf{Software Engineer}, Apple -- Cupertino, CA\end{twocolentry}

\vspace{0.10 cm}
\begin{onecolentry}
    \begin{highlights}
        \item Reduced time to render user buddy lists by 75\% by implementing a prediction algorithm
        \item Integrated iChat with Spotlight Search by creating a tool to extract metadata from saved chat transcripts and provide metadata to a system-wide search database
        \item Redesigned chat file format and implemented backward compatibility for search
    \end{highlights}
\end{onecolentry}

\vspace{0.2 cm}
```
While every language syntax serves different purposes and has unique trade-offs in conciseness vs. expressiveness, it is kind of absurd that we need to close each begin with a corresponding end (same issue with XML).
And, often we need to manually include boilerplate code for each section, like the `vspace` and the `twocolentry` and `onecolentry` environments.
These don't convey the intent of the document, rather they are implementation details we don't want to deal with.

### Tooling
Another issue is with the language server support for LaTeX.
This is similar to the previous issue, where we really need to do active research if you want to add something in LaTeX.
For example, if you want to add a separator, you can't just type `separator` and expect the language server (and even the documentation) to understand what you mean.
Instead, you likely have to ask an LLM or look online before you finally find the correct syntax `\hrulefill`.

## Typst: the solution
So, realizing that LaTeX may be too complex of a tool for writing resumes, I decided to try out Typst.
The first step is finding a suitable resume template.
Fortunately, there are already some good-looking templates out there, such as [modern-cv](https://typst.app/universe/package/modern-cv/), so I decided to use it as a starting point.

### Benefits
The great thing about Typst is that it is a **declarative language**.
This is, in my opinion, a huge improvement for the purposes of writing a resume or any document, as it allows me to focus on the writing the content rather than how to use the tool.
For example, instead of explicitly defining the layout and formatting, we can use the format by importing the `modern-cv` package and using its predefined `resume` style.
```typst
#show: resume.with(
  author: (
    firstname: "Steven",
    lastname: "Cao",
    email: "s3cao@uwaterloo.ca",
    website: "caohc.me",
    // ...
  ),
)
```
Compared to LaTeX, this is much cleaner and, more importantly, it is a lot more intuitive especially for those who have used a language with a similar style (JS, Kotlin, etc.).
If I want to change the details, the template is clearly laid out and it's easy to imagine how to modify it.
While all of this can be achieved with LaTeX, Typst's inherent declarative nature makes it much simpler to set this up.

## Modifying the template
Now, I do have a few issues with the `modern-cv` template out of the box, namely that it is colored and I don't like some of the layout choices.
Again, Typst makes it very easy to modify the inner workings of the template.
Here's how I changed the template:

### Colors
Removing the colors is fairly easy, as the color palette is already defined in the template, so I can simply set all these colors to black.

### Separator
I didn't like how the separator line begins after the section/heading title.
To change this, I redefined `heading` to place a fullwidth line in a `box` after the heading:
```typst
#let resume(/*...*/) = {
  // ...
  show heading: it => [
    #set text(
      weight: "thin",
    )
    #set align(left)
    #set block(above: 1em)
    #block(spacing: 0.4em)[
      #smallcaps[#strong[#text(color)[#it.body]]] // heading text
    ]
    #box(width: 1fr, line(length: 100%)) // separator line
  ]
  // ...
}
```
`box` is an easy way to create a paragraph-like element in Typst.

### Job title entry
Another issue was the two-lined job title heading, which in my opinion took up too much space for a single-paged resume.
So, I compressed the job title to use a single line with the following format similar to my previous resume template:
```typst
#let resume-entry(
  title: none,
  start-date: "",
  end-date: "",
  description: "",
  title-link: none,
) = {
  let title-content = [
    #strong[#title]
    #if type(title-link) == str [
      #link(title-link)[#fa-link()]
    ]
    #if description != "" [
      ---
      #emph[#description]
    ]
  ]
  let date = [
    #if start-date == "" {
      end-date
    } else {
      [
        #start-date
        ---
        #end-date
      ]
    }
  ]
  block(above: 1em, below: 0.65em)[
    #pad[
      #lr-header(title-content, date)
    ]
  ]
}
```
where `lr-header` creates a line that contains both left-aligned and right-aligned content.
In addition to being single-lined, this `resume-entry` function allows all the components of a job entry to be specified, with the layout details hidden in the template file.
Often, when we want to edit the resume, we either want to edit the content or the layout design.
In that case, we only need to edit one of the modules.
For those who know object-oriented programming, this is similar to the concept of encapsulation.

## Conclusion
I've made a Typst resume template designed to be simple, easy to use, and very maintainable, taking advantage of Typst's clean syntax and declarative style.
By separating the resume into two parts, the content and the layout design, this template becomes very easy to customize and maintain.

You can check out the complete source code on [GitHub](https://github.com/UltimateBoomer/simple-cs-resume).
Provided are also some sample resumes you can use based on my template.

# SpineAI Engineering Documentation

Internal documentation for all SpineAI development and engineering.

TODO(billy): Split into separate pages.

# Documentation Philosphy

Back in the dark ages, there was no documentation. Billy saw that this was a
problem and created the first Outline, based upon the way he saw things in his
mind:

- **Application**
    - The high level understanding of the application and its parts.
- **Development**
    - The work done by developers to design, create, and test the application.
- **Production**
    - The actual process of running and delivering the application to end users.

TODO(billy): SpineAI tree/mind map image.


# Application

This section explains the blocks that make up the SpineAI Application.

## Introduction

The SpineAI application, abstractly, consists of 4 main components:

- Machine Learning
- Backend
- API
- Frontend

TODO(billy): Create a SpineAI block diagram.

TODO(billy): Consider a world where the backend is stateless.

## Machine Learning

## Backend

## API

## Frontend

# Development

## Introduction

TODO(billy): Intro, philosophy (design, testing, maintenance, close to production, etc.), etc.

## Collaboration

Engineering is at its core a social and creative endeavor. Before even writing
your first line of code, it helps to know what resources we use to organize
and collaborate. (eg. ClickUp)

## Environment

This section explains first time setup of the SpineAI development environment.

### Machine Learning

### Backend

### API

### Fronend

### Pre-production (Docker)

## Contribution

To maintain our code quality and reduce maintence costs and technical debt, we
run all our code through automated tests (pre and post-submit), and through a
manual code review process.

# Production

## Containerization (Docker)

In ye olden days, software was simple.

Developers manually set up physical computers, and ran their software on those
computers. If the code or requirements changed, developers would simply go to
that machine and make the required changes.

Now, software is increasingly complicated to install, with hundreds or thousands
of dependencies. Even worse, systems may comprise of hundreds of machines,
virtual or physical, and manual management quickly becomes impossible.

Enter containerization.

## Local Infrastructure

## Cloud Infrastructure

### AWS

### Current Instances

## Pre-production Validation and Testing

TODO(billy): Canarys, tests, etc.

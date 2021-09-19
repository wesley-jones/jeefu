# Contributing to Jeefu

Code contributions should be submitted in the form of a pull request. Here are the steps:

* Make sure that there is an issue tracking your work.
* Create a [fork](https://help.github.com/articles/fork-a-repo/) of the repository and clone it to your development environment.
* Make a new branch for your code off of the `dev` branch.
* Create an environment and install necessary requirements: `requirements.txt`
* Start writing code!


### Committing Guidelines
Commit messages should have a subject line, separated by a blank line and then 
paragraphs of approximately 72 char lines. For the subject line, shorter is better --
ideally 72 characters maximum. In the body of the commit message, more detail
is better than less. See [Chris Beams](https://chris.beams.io/posts/git-commit/) for
more guidelines about writing good commit messages.

* Tag the issue number in your subject line. For Github issues, it's helpful to 
use the abbreviation ("GH") to separate it from Jira tickets.
    ```
    GH #1111 - Add commit message guidelines

    This contains more detailed information about the feature
    or bugfix. It's written in complete sentences. It has
    appropriate capitalization and punctuation. It's separated
    from the subject by a blank line.
    ```
* Limit commits to the most granular changes that make sense. Group together small
units of work into a single commit when applicable. Think about readability;
your commits should tell a story about your changes that everyone can follow. 

### Making a Pull Request
* Target the dev branch
* Use a brief but descriptive title.
* Include `Relates to: #issue_number` and a short description of your changes in the
body of the pull request.
Do not merge the pull request. The code maintainer will review the code, request any changes, and once all requests have been completed, the code maintainer will merge the pull request.

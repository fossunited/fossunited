# Documentation

One way to get involved with the project is to add and improve the
documentation of the project. As the Community grows, the numbers of people
who will be attending, the number of events, and the overall activity on the
Platform is expected to grow. Clear and concise documentation ensures that the
team is able to effectively communicate how the Platform should be used to the
respective audience.

As you can see, a part of the documentation is meant for volunteers who
actively manage events and such in the Community and the rest of the
documentation is oriented meant for the rest of the Community for example, event
participants. Please keep this in mind when adding or improving the
documentation.

The documentation is built from [Markdown](https://www.markdownguide.org/)
files in the [FOSS UNITED GitHub](https://github.com/fossunited/fossunited/tree/develop/docs)
repository. The documentation is built using the [Zensical](https://github.com/zensical/zensical)
SSG. Every time changes are made in the `develop` branch to the `docs/*`
folder on the Git repository, a [GitHub Action](https://github.com/fossunited/fossunited/blob/develop/.github/workflows/docs.yml)
gets triggered, which builds and pushes the documentation to the `gh-pages`
branch, to be served using [GitHub pages](https://docs.github.com/en/pages).

## Steps to build documentation locally

1. `cd` into docs directory

2. Install [Zensical](https://zensical.org/docs/get-started/#install-with-uv) via `uv` package manager

    ```sh
    uv add zensical pre-commit
    ```

3. Setup pre-commit hook

	```sh
    pre-commit install
	```

This enables spell and grammar check for docs content via [vale](https://vale.sh).

4. Build and serve the docs at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

    ```sh
    zensical serve
    ```

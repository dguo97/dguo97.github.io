# dguo97.github.io

Source code for the personal academic website of David Guo, published at **https://dguo97.github.io**.

The site is built with [Jekyll](https://jekyllrb.com/) and hosted on GitHub Pages. It is based on the [Academic Pages](https://github.com/academicpages/academicpages.github.io) template.

## Editing the site

Most changes only need a text edit in one of these places:

| Path | What it controls |
|---|---|
| `_config.yml` | Site-wide settings: name, bio, social links, site title |
| `_pages/` | Main pages (about, CV, and so on) |
| `_publications/`, `_talks/`, `_teaching/`, `_portfolio/` | One Markdown file per entry in each section |
| `_posts/` | Blog posts |
| `_data/` | Navigation menu and other site data |
| `images/`, `files/`, `assets/` | Pictures, downloadable files, and styles/scripts |
| `CV.pdf` and other PDFs in the root | Documents linked from the site |

After editing, commit and push. GitHub Pages rebuilds the site automatically, and changes usually appear within a couple of minutes.

## Running locally

To preview changes before pushing, you need Ruby, Bundler and Node.js.

```bash
git clone https://github.com/dguo97/dguo97.github.io.git
cd dguo97.github.io
bundle install
bundle exec jekyll serve -l -H localhost
```

Then open http://localhost:4000. The preview rebuilds automatically when you save a file. If `bundle install` fails, delete `Gemfile.lock` and try again.

### With Docker

If you would rather not install Ruby, the included `Dockerfile` can run the site:

```bash
docker build -t jekyll-site .
docker run -p 4000:4000 --rm -v $(pwd):/usr/src/app jekyll-site
```

On Windows PowerShell, replace `$(pwd)` with `${PWD}`.

## Credits and licence

This site uses the Academic Pages template, which was forked from the [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) Jekyll theme by Michael Rose. Both are released under the MIT licence. See [LICENSE](LICENSE).

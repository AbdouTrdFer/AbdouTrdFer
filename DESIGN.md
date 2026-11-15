# Design notes — the light edition

A light, open profile for Abdelali Ferhan: white surfaces, soft blue, lavender, mint, and a little warm sand. The banner leads with his name and role. The illustration and slow floating motion suggest a developer's workbench. Whitespace, readable copy, and recognizable technology icons make the page easy to scan.

The sequence is introduction → about → toolkit → selected work → activity → contact. Short project descriptions explain the value of each build; contact links appear near the introduction and at the end. The profile uses ordinary GitHub Markdown/HTML, so the layout does not depend on scripts or custom page CSS.

## Research and inspiration

- [Bosaj's README source](https://github.com/Bosaj/Bosaj/blob/main/README.md): inspected the actual source and its banner, navigation, biography, technology icons, and analytics. Those structural ideas inform this profile's hierarchy. Its personal history, artwork, banner, and writing are not reused.
- [Awesome GitHub Profile README](https://github.com/abhisheknaiidu/awesome-github-profile-readme): surveyed clean and animated developer profiles.
- [DenverCoder1](https://github.com/DenverCoder1/DenverCoder1): a clear introduction and easy-to-find contact links alongside activity data.
- [Skill Icons](https://github.com/tandpfun/skill-icons): the light technology-logo rows are downloaded and hosted locally. The accompanying license is in `assets/skill-icons-LICENSE.txt`.

All banner artwork, workspace illustration, project illustrations, buttons, dividers, footer, and dashboard graphics are original code-generated vectors. `scripts/build_art.py` regenerates the original artwork. `scripts/render_preview.py` renders the banner as a GIF. The technology logos are the credited third-party exception.

## Data and accessibility

- Profile facts and project descriptions come from the existing profile and local portfolio. Education and location use the portfolio's existing information. No professional tenure, employer, or performance claim is invented.
- The dashboard retains GitHub's reported aggregate, breakdown, and daily series. GitHub may return a small discrepancy between its total and the sum of daily cells; the renderer preserves the source data rather than adding activity.
- Push events have a separate limited window and are never added to contribution totals.
- Key information remains selectable text, with image alt text for illustrations and stats.
- Static artwork is selected for reduced motion. Phone screens receive a reflowed name banner and a taller dashboard.
- White image surfaces remain legible in both GitHub themes. The local preview opens in light mode and also checks dark mode.
- Project art communicates a category; it is not an application screenshot.

## Platform references

- [GitHub profiles](https://docs.github.com/en/account-and-profile/concepts/personal-profile)
- [Contribution criteria](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)
- [GraphQL users and contribution collections](https://docs.github.com/en/graphql/reference/users)
- [Public events and their limits](https://docs.github.com/en/rest/activity/events)
- [Workflow token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)
- [Komarev profile views](https://github.com/antonkomarev/github-profile-views-counter)

The local preview approximates GitHub's content column. The published profile must also be inspected because GitHub controls spacing, image caching, and Markdown rendering.

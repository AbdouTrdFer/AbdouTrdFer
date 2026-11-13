# Design notes — Abdelali Ferhan

An engineering studio identity: deep green-black, warm white, lime, and restrained secondary colors. The original AF monogram sits inside an orbital system: interfaces and infrastructure as connected parts of one product. Motion stays in two deliberate places, leaving the biography and project descriptions easy to read.

The sequence is identity → approach → selected work → toolkit → evidence → contact. Content uses the existing profile screenshot, the local portfolio, and verified public repository links. No designer job title, professional tenure, client result, or expertise score has been invented.

## Research and inspiration

- [Awesome GitHub Profile README](https://github.com/abhisheknaiidu/awesome-github-profile-readme): surveyed its range of minimal, animated, and data-oriented profiles.
- [DenverCoder1's profile source](https://github.com/DenverCoder1/DenverCoder1): clear role introduction, animation, discoverable contact links, and project emphasis. These structural ideas informed the hierarchy; its assets and text were not copied.
- [ryo-ma's profile](https://github.com/ryo-ma/ryo-ma): contribution and project metrics as visual evidence. This design uses its own dashboard rather than a stack of differently styled widgets.
- [Pretty GitHub](https://github.com/Jenesyx/pretty-github): consistent artwork and editable, repository-owned profile assets.

All hero graphics, project illustrations, buttons, process art, and dashboard artwork in this package are original code-generated vectors. The GIFs are rendered from that source. There are no borrowed character GIFs, stock illustrations, or copied banners.

## Data and platform references

- [GitHub profile documentation](https://docs.github.com/en/account-and-profile/concepts/personal-profile): profile README and supported images/GIFs.
- [GitHub contribution reference](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference): contribution criteria and visibility.
- [GraphQL user reference](https://docs.github.com/en/graphql/reference/users): contribution collection and calendar fields.
- [REST events documentation](https://docs.github.com/en/rest/activity/events): public push-event feed and its retention/cap limits.
- [Workflow token documentation](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token): automatic token and scoped permissions.
- [Komarev views counter](https://github.com/antonkomarev/github-profile-views-counter): the external view badge.

## Visual and accessibility choices

- Artwork uses a solid background so it remains legible in both GitHub themes.
- Essential profile information and project descriptions remain selectable text.
- Images have alt text; static alternatives are provided for reduced motion.
- The stats snapshot is linked to the actual GitHub overview and shows its date range and freshness.
- Project illustrations communicate the project category; they are not presented as application screenshots.
- The initial real snapshot deliberately leaves authenticated-only breakdowns unavailable. Test fixtures are confined to tests, never used as profile data.

The previews approximate GitHub's content column. They are not screenshots of a published GitHub profile. The daily authenticated workflow must be verified after installation in the actual profile repository.

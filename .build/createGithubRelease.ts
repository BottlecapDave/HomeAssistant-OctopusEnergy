async function createGithubRelease(githubToken: string, githubOwnerRepo: string, tag: string, notes: string) {
  if (!githubToken) {
    throw new Error('Github token not specified');
  }

  if (!githubOwnerRepo) {
    throw new Error('Github owner/repo not specified');
  }

  if (!tag) {
    throw new Error('Tag not specified');
  }

  if (!notes) {
    throw new Error('Notes not specified');
  }

  const response = await fetch(
    `https://api.github.com/repos/${githubOwnerRepo}/releases`,
    { 
      method: 'POST',
      headers: {
        "Accept": "application/vnd.github+json",
        "Authorization": `Bearer ${githubToken}`,
        "X-GitHub-Api-Version": "2022-11-28" 
      },
      body: `{"tag_name":"${tag}","name":"${tag}","body":"${notes}","draft":false,"prerelease":false}`
    }
  );
}

createGithubRelease(
  process.env.GITHUB_TOKEN,
  process.env.GITHUB_REPOSITORY,
  process.argv[2],
  `${process.argv[3]}\n${process.env.RELEASE_BODY_APPENDIX}`
).then(() => console.log('Success'));
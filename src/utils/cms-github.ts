// portfolio.jsx
export async function getServerSideProps() {
  const redis = new Redis(process.env.REDIS_URL);
  const cache = await redis.get("repositories");
  if (cache !== null)
    return {
      props: {
        repositories: cache,
      },
    };
  const response = await fetch("https://api.github.com/users/GITHUB_USERNAME/repos", {
    headers: {
      authorization: `token ${process.env.GITHUB_PAT}`,
    },
  });
  const json = await response.json();
  const repositories = json
    .map((repo) => {
      if (!repo.topics.includes("portfolio")) return null;
      if (repo.archived) return null;
      return repo;
    })
    .filter((project) => project !== null);
  redis.set("repositories", JSON.stringify(repositories));
  return {
    props: {
      repositories,
    },
  };
}
export default function Page({ repositories }) {
  // return (
  //     // <pre>
  //     //     // {JSON.stringify(repositories, null, 4)}}
  //     // </pre>
  // );
}

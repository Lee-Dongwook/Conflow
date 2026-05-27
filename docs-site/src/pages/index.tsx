import clsx from "clsx";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import Heading from "@theme/Heading";
import styles from "./index.module.css";

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx("hero hero--primary", styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro"
          >
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}

const features = [
  {
    title: "AI Meeting Summary",
    description:
      "Huddle voice meeting transcripts are automatically summarized into structured action items and decisions.",
  },
  {
    title: "Multi-Agent System",
    description:
      "LangGraph-based supervisor orchestrates specialized agents for meeting summaries, blocker detection, and retrospective insights.",
  },
  {
    title: "A2UI-Ready Architecture",
    description:
      "Headless business logic decoupled from the UI, enabling AI agents to invoke any feature programmatically.",
  },
];

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title="Home" description={siteConfig.tagline}>
      <HomepageHeader />
      <main>
        <section className={styles.features}>
          <div className="container">
            <div className="row">
              {features.map((feat, idx) => (
                <div key={idx} className={clsx("col col--4")}>
                  <div className="text--center padding-horiz--md padding-vert--lg">
                    <Heading as="h3">{feat.title}</Heading>
                    <p>{feat.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}

import { ResearchApp } from "@/features/research/research-app";
import { notFound } from "next/navigation";
export function generateStaticParams() {
  return ["macro", "sectors", "relationships", "learn"].map((section) => ({
    section,
  }));
}
export default async function SectionPage({
  params,
}: {
  params: Promise<{ section: string }>;
}) {
  const { section } = await params;
  if (!["macro", "sectors", "relationships", "learn"].includes(section))
    notFound();
  return <ResearchApp section={section} />;
}

import Navbar from "@/components/shared/Navbar";
import PageWrapper from "@/components/shared/PageWrapper";
import Badge from "@/components/shared/Badge";

export default function Home() {
  return (
    <>
      <Navbar />
      <PageWrapper>
        <div className="py-8 flex gap-2">
          <Badge variant="persona">Adventure</Badge>
          <Badge variant="budget">Budget</Badge>
        </div>
      </PageWrapper>
    </>
  );
}

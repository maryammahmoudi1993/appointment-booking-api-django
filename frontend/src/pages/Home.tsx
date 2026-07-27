import {
  HeroSection,
  PortfolioDemoBar,
  ServiceCategoryBar,
  WhyChooseUs,
  ServicesGrid,
  AboutSection,
  HowItWorks,
  PromoBanner,
  GalleryAndTestimonials,
} from "../components/landing";
import Reveal from "../components/ui/Reveal";
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { user } = useAuth();
  return (
    <div className="overflow-hidden bg-main">
      {!user && <PortfolioDemoBar />}
      <HeroSection />
      <Reveal>
        <ServiceCategoryBar />
      </Reveal>
      <Reveal>
        <WhyChooseUs />
      </Reveal>
      <Reveal>
        <ServicesGrid />
      </Reveal>
      <Reveal>
        <AboutSection />
      </Reveal>
      <Reveal>
        <HowItWorks />
      </Reveal>
      <Reveal>
        <PromoBanner />
      </Reveal>
      <Reveal>
        <GalleryAndTestimonials />
      </Reveal>
    </div>
  );
}

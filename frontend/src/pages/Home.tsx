import {
  HeroSection,
  ServiceCategoryBar,
  WhyChooseUs,
  ServicesGrid,
  AboutSection,
  HowItWorks,
  PromoBanner,
  GalleryAndTestimonials,
} from "../components/landing";
import Reveal from "../components/ui/Reveal";

export default function Home() {
  return (
    <div className="overflow-hidden bg-main">
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

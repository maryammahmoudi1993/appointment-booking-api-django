import {
  HeroSection,
  ServiceCategoryBar,
  WhyChooseUs,
  ServicesGrid,
  AboutSection,
  HowItWorks,
  PromoBanner,
  GalleryAndTestimonials,
  BookingWidgetSection,
  FinalCta,
} from "../components/landing";
import Reveal from "../components/ui/Reveal";

export default function Home() {
  return (
    <div>
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
      <Reveal>
        <BookingWidgetSection />
      </Reveal>
      <Reveal>
        <FinalCta />
      </Reveal>
    </div>
  );
}

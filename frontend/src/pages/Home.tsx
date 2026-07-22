import {
  HeroSection,
  ServicesGrid,
  AboutSection,
  GalleryAndTestimonials,
  BookingWidgetSection,
} from "../components/landing";

export default function Home() {
  return (
    <div>
      <HeroSection />
      <ServicesGrid />
      <AboutSection />
      <GalleryAndTestimonials />
      <BookingWidgetSection />
    </div>
  );
}

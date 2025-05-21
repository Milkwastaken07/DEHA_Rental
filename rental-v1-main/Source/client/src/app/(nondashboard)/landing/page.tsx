"use client";
import React from 'react';
import HeroSection from './HeroSection';
import FeaturesSection from './FeaturesSection';
import DiscoverSection from './DiscoverSection';
import CallToActionSection from './CallToActionSection';
import FooterSection from './FooterSection';
import { useGetAuthUserQuery } from '@/state/api';


const LandingPage = () => {
  const {data: authUser} = useGetAuthUserQuery();
  console.log("authUser: ", authUser);
  return (
    <div>
     <HeroSection/>
     <FeaturesSection/>
     <DiscoverSection/>
     <CallToActionSection/>
     <FooterSection/>
    </div>
  );
}

export default LandingPage;
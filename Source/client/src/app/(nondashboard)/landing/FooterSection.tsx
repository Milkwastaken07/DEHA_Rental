import Link from 'next/link'
import React from 'react'
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome"
import {
    faFacebook,
    faInstagram,
    faTwitter,
    faLinkedin,
    faYoutube
} from "@fortawesome/free-brands-svg-icons"
import { icon } from '@fortawesome/fontawesome-svg-core'

const contactLinks = [
    {
        href: "#",
        icon: faFacebook,
        ariaLabel: "Facebook"
    },
    {
        href: "#",
        icon: faInstagram,
        ariaLabel: "Instagram"
    },
    {
        href: "#",
        icon: faTwitter,
        ariaLabel: "Twitter"
    },
    {
        href: "#",
        icon: faLinkedin,
        ariaLabel: "Linkedin"
    },
    {
        href: "#",
        icon: faYoutube,
        ariaLabel: "Youtobe"
    }
]

const FooterSection = () => {
    
  return (
    <footer className='border-t border-gray-200 py-20'>
        <div className='max-w-4xl mx-auto px-6 sm:px-8'>
            <div className='flex flex-col md:flex-row justify-between items-center'>
                <div className='mb-4'>
                    <Link href="/" className='text-xl font-bold uppercase'>
                        RENTIFULL
                    </Link>
                </div>
                <nav className='mb-4'>
                    <ul className='flex space-x-6'>
                        <li>
                            <Link href="/about">About Us</Link>
                        </li>
                        <li>
                            <Link href="/contact">Contact Us</Link>
                        </li>
                        <li>
                            <Link href="/faq">FAQ</Link>
                        </li>
                        <li>
                            <Link href="/terms">Terms</Link>
                        </li>
                        <li>
                            <Link href="/privacy">Privacy</Link>
                        </li>
                    </ul>
                </nav>
                <div className='flex space-x-4 mb-4'>
                    {contactLinks.map((item, index) => (
                        <a
                        key={index}
                        href={item.href}
                        aria-label={item.ariaLabel}
                        className='hover:text-primary-600'
                        >
                            <FontAwesomeIcon icon={item.icon}  className='h-6 w-6'/>
                        </a>
                    ))}
                </div>
                <div className='mt-8 text-center text-sm text-gray-500 flex justify-center space-x-4'>
                    <span>RENTiful. All rights reserved.</span>
                    <Link href="privacy">Privacy Policy</Link>
                    <Link href="/terms">Terms of Service</Link>
                    <Link href="/cookies">Cookie Policy</Link>
                </div>
            </div>
        </div>
    </footer>
  )
}

export default FooterSection
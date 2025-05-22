"use client";
import React from 'react'
import {motion} from "framer-motion"
import Image from 'next/image';
import Link from 'next/link';

const containerVariants = {
    hidden: {opacity: 0},
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.2
        }
    }
} 

const itemVariants = {
    hidden: {opacity: 0, y: 20},
    visible: {opacity: 1, y: 0}
}

const data = [
    {
        imageSrc: "/landing-icon-wand.png",
        title: "Search for Properties",
        description: "Browse through our extensive collection of rental properties in your desired location"
    },
    {
        imageSrc: "/landing-icon-calendar.png",
        title: "Book Your Rental",
        description: "Once you've found the perfect rental property, easily book it online with just a few clicks"
    },
    {
        imageSrc: "/landing-icon-heart.png",
        title: "Search for Properties",
        description: "Move into your new rental property and start enjoying your dream home."
    }

]

const DiscoverSection = () => {
  return (
    <motion.div
     initial="hidden"
     whileInView="visible"
     viewport={{once: true, amount: 0.8}}
     variants={containerVariants}
     className='py-12 px-6 bg-white mb-16'
    >
        <div className='max-w-6xl xl:max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 xl:px-16'>
            <motion.div
                variants={itemVariants}
                className='my-12 text-center'
            >
                <h2 className='text-3xl font-semibold leading-tight text-gray-800'>
                    Discover
                </h2>
                <p className='mt-4 text-lg text-gray-600'>
                    Find your Dream Rental Property Today!
                </p>
                <p className='mt-2 text-gray-500 max-w-3xl mx-auto'>
                    Lorem ipsum dolor, sit amet consectetur adipisicing elit. Veritatis neque deleniti, nemo iste qui aut accusantium officia sapiente ratione tenetur ad numquam aliquam itaque culpa! Asperiores incidunt voluptatum ipsam cumque nostrum, praesentium amet voluptas omnis dolor impedit nemo atque modi quos corporis fuga tempora, repellendus aliquam, inventore qui animi eius.
                </p>
            </motion.div>
            <div className='grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12 xl:gap-16 text-center'>
                {data.map((card, index) => (
                    <motion.div key={index} variants={itemVariants}>
                        <DiscoverCard {...card}/>
                    </motion.div>
                ))}
            </div>
        </div>
    </motion.div>
  )
}

const DiscoverCard = ({
    imageSrc,
    title,
    description
}: {
    imageSrc: string;
    title:string;
    description: string;
}) => (
    <div className='px-4 py-12 shadow-lg rounded-lg bg-primary-50 md:h-72'>
        <div className='bg-primary-700 p-[0.6rem] rounded-full mb-4 h-10 w-10 mx-auto'>
        <Image src={imageSrc}
         width={30}
         height={30}
         className='w-full h-full object-contain'
         alt={title}
        />
        </div>
        <h3 className='mt-4 text-xl font-medium text-gray-800'>{title}</h3>
        <p className='mt-2 text-base text-gray-700'>{description}</p>
    </div>
)

export default DiscoverSection;
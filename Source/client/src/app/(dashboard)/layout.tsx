"use client"
import Navbar from '@/components/Navbar';
import { SidebarProvider } from '@/components/ui/sidebar';
import Sidebar from "@/components/AppSidebar"
import { NAVBAR_HEIGHT } from '@/lib/constants';
import React, { useEffect, useState } from 'react';
import { useGetAuthUserQuery } from '@/state/api';
import { usePathname, useRouter } from 'next/navigation';

const DashboardLayout = ({children}: {children: React.ReactNode}) => {
    const {data: authUser} = useGetAuthUserQuery();
    const router = useRouter();
    const pathname = usePathname();
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        if(authUser){
            const userRole = authUser.userRole?.toLowercase()
            if(
                (userRole === "manager" && pathname.startsWith("/search")) ||
                (userRole === "manager" && pathname === "/")
            ){
                router.push("managers/properties", {scroll: false});
            }else{
                setIsLoading(false);
            }
        }
    }, [authUser, router, pathname]);
    
    if (!authUser?.userRole) return null;

    return (
        <SidebarProvider>
            <Navbar />
            <div style={{paddingTop: `${NAVBAR_HEIGHT}px`}}>
                <main className='flex'>
                    <Sidebar userType={authUser?.userRole.toLowerCase()} />
                    <div className='flex-grow trasition-all duration-300'>
                        {children}
                    </div>
                </main>
            </div>
        </SidebarProvider>
    );
}

export default DashboardLayout;

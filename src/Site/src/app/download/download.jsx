"use client"

import { useEffect, useState } from 'react';
import { logEvent } from 'firebase/analytics';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

import { analytics } from '@/config/firebase';
import Windows from './sections/windows';
import Linux from './sections/linux';
import Mac from './sections/mac';

const DownloadPage = () => {

    const [tabValue, setTabValue] = useState(0);

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue);
    };

    useEffect(() => {
        logEvent(analytics, 'download_page_viewed', {
            page_location: window.location.href,
            page_path: window.location.pathname,
            page_title: document.title
        });
    }, []);

    return (
        <div className='download-page'>
            <article className='download-container'>
                <h1 className='download-title'>Download and install StreamStorm</h1>
                <span className='download-description'>Select your operating system</span>
                <Tabs value={tabValue} onChange={handleTabChange} centered>
                    <Tab label="Windows" />
                    <Tab label="Linux" />
                    <Tab label="Mac" />
                </Tabs>
                <div className='download-sections'>
                    {
                        tabValue === 0 ? (
                            <Windows />
                        ) : tabValue === 1 ? (
                            <Linux />
                        ) : (
                            <Mac />
                        )
                    }
                </div>

            </article>

        </div>
    )

}

export default DownloadPage
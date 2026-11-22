"use client";
import { createContext, useContext, useEffect, useState } from 'react';
import { httpsCallable } from 'firebase/functions';
import { functions } from '../config/firebase';

import * as atatus from '../config/atatus';

const DownloadCountContext = createContext();

const DownloadCountProvider = ({ children }) => {
    const [downloadCount, setDownloadCount] = useState(null);

    const downloadCountFunction = httpsCallable(functions, 'downloads_count');

    const fetchDownloadCount = async () => {
        atatus.startOperation('fetch_download_count');
        atatus.startDurationVital('fetch_download_count');

        downloadCountFunction({ mode: 'get' })
            .then((result) => {
                atatus.stopDurationVital('fetch_download_count');
                if (result?.data?.success) {
                    atatus.succeedOperation('fetch_download_count');
                    atatus.downloadLogger.info('Fetched download count', { count: result.data.count });
                    atatus.setGlobalContextProperty('downloadCount', result.data.count);
                    setDownloadCount(result.data.count);
                } else {
                    atatus.failOperation('fetch_download_count', 'Download count function unsuccessful');
                    atatus.addError(new Error('Failed to fetch download count'), {
                        receivedData: result?.data,
                        tags: ['download_count_fetch_error']
                    });
                    atatus.downloadLogger.warn('Failed to fetch download count', { receivedData: result?.data });
                }
            })
            .catch((error) => {
                atatus.stopDurationVital('fetch_download_count');
                atatus.failOperation('fetch_download_count', error.message);
                atatus.addError(error, { tags: ['download_count_fetch_error'] });
                atatus.downloadLogger.error('Error fetching download count', { error: error.message });
            });
    };

    const updateDownloadCount = async () => {
        atatus.addAction('download-count-increment-triggered');
        atatus.startOperation('increment_download_count');
        atatus.startDurationVital('increment_download_count');

        downloadCountFunction({ mode: 'set' })
            .then((result) => {
                atatus.stopDurationVital('increment_download_count');
                if (result?.data?.success) {
                    atatus.succeedOperation('increment_download_count');
                    atatus.downloadLogger.info('Incremented download count', { count: result.data.count });
                    atatus.setGlobalContextProperty('downloadCount', result.data.count);
                    setDownloadCount(result.data.count);
                } else {
                    atatus.failOperation('increment_download_count', 'Update function unsuccessful');
                    atatus.addError(new Error('Failed to update download count'), {
                        receivedData: result?.data,
                        tags: ['download_count_update_error']
                    });
                    atatus.downloadLogger.warn('Failed to update download count', { receivedData: result?.data });
                }
            })
            .catch((error) => {
                atatus.stopDurationVital('increment_download_count');
                atatus.failOperation('increment_download_count', error.message);
                atatus.addError(error, { tags: ['download_count_update_error'] });
                atatus.downloadLogger.error('Error updating download count', { error: error.message });
            });
    };

    useEffect(() => {
        fetchDownloadCount();
    }, []);

    const exports = {
        downloadCount,
        updateDownloadCount
    };

    return (
        <DownloadCountContext.Provider value={exports}>
            {children}
        </DownloadCountContext.Provider>
    );
};

const useDownloadCount = () => useContext(DownloadCountContext);

export {
    useDownloadCount,
    DownloadCountProvider
};

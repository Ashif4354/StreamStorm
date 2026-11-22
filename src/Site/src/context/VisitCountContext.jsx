"use client";
import { createContext, useContext, useEffect, useState } from 'react';
import { httpsCallable } from 'firebase/functions';
import { functions } from '../config/firebase';

import * as atatus from '../config/atatus';

const VisitCountContext = createContext();

const VisitCountProvider = ({ children }) => {
    const [visitCount, setVisitCount] = useState(null);

    const visitCountFunction = httpsCallable(functions, 'visit_count');

    const fetchVisitCount = async () => {
        atatus.startOperation('fetch_visit_count');
        atatus.startDurationVital('fetch_visit_count');

        visitCountFunction()
            .then((result) => {
                atatus.stopDurationVital('fetch_visit_count');
                if (result?.data?.success) {
                    atatus.succeedOperation('fetch_visit_count');
                    atatus.visitLogger.info('Fetched visit count', { count: result.data.count });
                    atatus.setGlobalContextProperty('visitCount', result.data.count);
                    setVisitCount(result.data.count);
                } else {
                    atatus.failOperation('fetch_visit_count', 'Visit count function unsuccessful');
                    atatus.addError(new Error('Failed to fetch visit count'), {
                        receivedData: result?.data,
                        tags: ['visit_count_fetch_error']
                    });
                    atatus.visitLogger.warn('Failed to fetch visit count', { receivedData: result?.data });
                }
            })
            .catch((error) => {
                atatus.stopDurationVital('fetch_visit_count');
                atatus.failOperation('fetch_visit_count', error.message);
                atatus.addError(error, { tags: ['visit_count_fetch_error'] });
                atatus.visitLogger.error('Error fetching visit count', { error: error.message });
            });
    };

    useEffect(() => {
        fetchVisitCount();
    }, []);

    return (
        <VisitCountContext.Provider value={visitCount}>
            {children}
        </VisitCountContext.Provider>
    );
};

const useVisitCount = () => useContext(VisitCountContext);

export { useVisitCount, VisitCountProvider };

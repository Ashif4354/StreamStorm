import OverView from '../components/OverView';
import Features from '../components/Features';
import Disclaimer from '../components/Disclaimer';

const HomePage = () => {
    return (
        <main className="main-content-container">
            <article>
                <OverView />
                <Features />
                <Disclaimer />
            </article>
        </main>
    );
};

export default HomePage;
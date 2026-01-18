
const Mac = () => {
    return (
        <section className='download-section'>
            <div className='download-section-title-container'>
                <h4 className='download-section-title'>Download for Mac</h4>
            </div>
            <span className="download-note">
                <i>macOS 10.13+</i>
            </span>

            <div className='mac-coming-soon'>
                <div className='coming-soon-icon'>🍎</div>
                <h5 className='coming-soon-title'>Dedicated macOS Build Coming Soon!</h5>
                <p className='coming-soon-description'>
                    A native macOS app is in the works. In the meantime, you can run StreamStorm directly from source code:
                </p>

                <div className='source-steps'>
                    <p className='step-intro'>🚀 <strong>Get started in just a few commands:</strong></p>
                    <ol className='steps-list'>
                        <li>
                            <strong>Install UV</strong> (Python dependency manager)<br />
                            <a href="https://docs.astral.sh/uv/getting-started/installation/" target="_blank" rel="noopener noreferrer">
                                📦 Get UV here
                            </a>
                        </li>
                        <li>
                            <strong>Clone the repository</strong>
                            <code className='code-block'>git clone https://github.com/Ashif4354/StreamStorm.git</code>
                        </li>
                        <li>
                            <strong>Navigate to StreamStorm</strong>
                            <code className='code-block'>cd StreamStorm</code>
                        </li>
                        <li>
                            <strong>Go to the Engine directory</strong>
                            <code className='code-block'>cd src/Engine</code>
                        </li>
                        <li>
                            <strong>Run StreamStorm</strong>
                            <code className='code-block'>uv run main.py</code>
                        </li>
                    </ol>
                    <p className='step-note'>✨ No Python or virtual environment setup needed — UV handles everything for you!</p>
                </div>
            </div>
        </section>
    )
};

export default Mac

const ErrorText = ({ errorText }) => {
    return (
        <div>
            {
                errorText && (
                    <div style={{ margin: ".5rem .5rem 0 .5rem" }}>
                        <span style={{ color: 'red', fontSize: '0.75rem' }}>
                            * {errorText}
                        </span>
                    </div>)
            }
        </div>


    );
}

export default ErrorText;
// export const atatusScript =`
//     (function (window, document) {
//         if (typeof window === 'undefined') return;

//         window._atatusConfig = {
//             apikey: "${process.env.NEXT_PUBLIC_ATATUS_RUM_API_KEY}"
//         };

//         // Load AtatusJS async
//         function _asyncAtatus(callback) {
//             const script = document.createElement("script");
//             script.type = "text/javascript";
//             script.async = true;
//             script.src = "https://dmc1acwvwny3.cloudfront.net/atatus-spa.js";

//             const firstScript = document.getElementsByTagName("script")[0];

//             if (script.addEventListener) {
//                 script.addEventListener("load", function (event) {
//                     callback(null, event);
//                 }, false);
//             }

//             firstScript.parentNode.insertBefore(script, firstScript);
//         }

//         _asyncAtatus(function () {
//             if (window.atatus) {
//                 console.log('Atatus analytics loaded successfully in Next.js');
//             }
//         });
//     })(window, document)`;
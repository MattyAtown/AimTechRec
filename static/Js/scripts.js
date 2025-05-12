const quotes = [
    "Ego is the anesthesia that deadens the pain of stupidity. — Rick Rigsby",
    "Whether you think you can or you think you can’t, you’re right. — Henry Ford",
    "The only way to do great work is to love what you do. — Steve Jobs",
    "The journey of a thousand miles begins with a single step. — Lao Tzu",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. — Winston Churchill",
    "Don’t count the days, make the days count. — Muhammad Ali",
    "Strive not to be a success, but rather to be of value. — Albert Einstein",
    "What you get by achieving your goals is not as important as what you become by achieving your goals. — Zig Ziglar",
    "Believe you can and you’re halfway there. — Theodore Roosevelt",
    "Dream big. Start small. Act now. — Robin Sharma"
];

const jobOfTheDay = "Job of the Day Alert - Senior AI Engineer at AiM Tech Recruitment";

let isJobOfTheDay = false;
let currentQuote = 0;

function updateBanner() {
    const quoteElement = document.getElementById("quote-banner");
    
    if (isJobOfTheDay) {
        quoteElement.textContent = jobOfTheDay;
        isJobOfTheDay = false;
    } else {
        quoteElement.textContent = quotes[currentQuote];
        currentQuote = (currentQuote + 1) % quotes.length;
        isJobOfTheDay = true;
    }
}

window.onload = () => {
    const quoteElement = document.getElementById("quote-banner");
    const today = new Date();
    const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 86400000);
    currentQuote = dayOfYear % quotes.length;
    quoteElement.textContent = quotes[currentQuote];
    setInterval(updateBanner, 60000);  // 60 seconds
};

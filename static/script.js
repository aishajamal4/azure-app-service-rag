const questionInput = document.getElementById("question");
const sendButton = document.getElementById("sendButton");
const chat = document.getElementById("chat");


function addMessage(text, type) {

    const message = document.createElement("div");

    message.className = `message ${type}`;

    message.textContent = text;

    chat.appendChild(message);

    chat.scrollTop = chat.scrollHeight;
}


async function sendQuestion() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    addMessage(question, "user");

    questionInput.value = "";

    sendButton.disabled = true;
    sendButton.textContent = "Loading...";


    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(data.error || "Request failed");
        }


        addMessage(data.answer, "bot");


    } catch (error) {

        addMessage(
            "Error: " + error.message,
            "bot"
        );

    } finally {

        sendButton.disabled = false;
        sendButton.textContent = "Send";

        questionInput.focus();
    }
}


sendButton.addEventListener(
    "click",
    sendQuestion
);


questionInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {
            sendQuestion();
        }

    }
);

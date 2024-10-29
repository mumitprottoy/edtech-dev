const updateProgressBar = () => {
    const totalAnswered = document.getElementById('total-answered');
    const totalAnswerable = document.getElementById('total-answerable');
    const progressBar = document.getElementById('progress-bar');
    const progress = Math.floor(parseInt((totalAnswered.innerText) / parseInt(totalAnswerable.innerText) * 100));
    console.log(progress);
    progressBar.style.width = progress.toString() + '%';
}

const updateAnswerCount = () => {
    const totalAnswered = document.getElementById('total-answered');
    totalAnswered.innerText = parseInt(totalAnswered.innerText) + 1;
    updateProgressBar();
}

const getAnswerSubmissionBaseURL = () => {
    const currentURL = document.location;
    const testKey = currentURL.href.split('/').at(-1);
    return `${currentURL.origin}/test/submit-answer/${testKey}`;
}

const submitAnswer = (answerID, optionID) => {
    const endpoint = `${getAnswerSubmissionBaseURL()}/${answerID}/${optionID}`;
    fetch(endpoint)
        .then(response => response.json())
            .then(message => {
                if (message.success) updateAnswerCount();
            })
}

const removeSlowly = (element) => {
    setTimeout(() => {
        element.remove();
    }, 500);
}


const processAnswer = (element) => {
    const toggledClassName = 'p m-2 brd-theme brd-l-bar rnd-1 grid-col-a-1';
    const optionID = element.id;
    const parent = element.parentElement.parentElement.parentElement.parentElement.parentElement;
    const answerID = parent.id;
    submitAnswer(answerID, optionID);
    const optionWrapper = element.parentElement.parentElement;
    optionWrapper.className = toggledClassName;
    [...optionWrapper.parentElement.children].forEach(child => {
        if (child != optionWrapper) child.className = 'hide';
    })
    element.setAttribute('onclick', '');
    
    // removeSlowly(parent);
    // if ([...document.getElementsByClassName(metaID)].length == 0) {
    //     grandParent.className = 'hide';
    //     removeSlowly(grandParent);
    // }
}



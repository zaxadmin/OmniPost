async function checkLocalAI() {
    try {
        if (window.ai && (await window.ai.canCreateTextSession()) === "readily") {
            return true;
        }
        return false;
    } catch (e) {
        return false;
    }
}
checkLocalAI();

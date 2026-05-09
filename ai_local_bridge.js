// Ce code détecte si l'appareil peut supporter l'IA locale
async function checkLocalAI() {
    if (window.ai && window.ai.canCreateTextSession) {
        const canCreate = await window.ai.canCreateTextSession();
        return canCreate === "readily";
    }
    return false;
}

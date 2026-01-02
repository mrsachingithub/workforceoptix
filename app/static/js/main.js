async function logout() {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST'
        });
        if (response.ok) {
            window.location.href = '/auth/login';
        }
    } catch (err) {
        console.error('Logout failed', err);
    }
}

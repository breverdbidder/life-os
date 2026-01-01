/**
 * WhatsApp Hub API Client
 * Handles communication with GitHub Actions and Supabase
 */

const API_CONFIG = {
    GITHUB_REPO: 'breverdbidder/life-os',
    GITHUB_TOKEN: '',
    SUPABASE_URL: 'https://mocerqjnksmhcjzxrewo.supabase.co',
    SUPABASE_ANON_KEY: '',
};

async function uploadWhatsAppExport(groupName, txtFile, mediaFiles = [], fetchMetadata = true, progressCallback = null) {
    try {
        if (progressCallback) progressCallback(10);
        const txtPath = await uploadFileToGitHub(txtFile, `whatsapp_exports/${groupName}/chat.txt`);
        if (progressCallback) progressCallback(30);
        
        const mediaPaths = [];
        if (mediaFiles.length > 0) {
            for (let i = 0; i < mediaFiles.length; i++) {
                const mediaPath = await uploadFileToGitHub(
                    mediaFiles[i],
                    `whatsapp_exports/${groupName}/media/${mediaFiles[i].name}`
                );
                mediaPaths.push(mediaPath);
                if (progressCallback) {
                    const progress = 30 + ((i + 1) / mediaFiles.length) * 40;
                    progressCallback(Math.round(progress));
                }
            }
        } else {
            if (progressCallback) progressCallback(70);
        }
        
        if (progressCallback) progressCallback(80);
        await triggerWhatsAppWorkflow(groupName, txtPath, mediaFiles.length > 0 ? `whatsapp_exports/${groupName}/media` : '', fetchMetadata);
        if (progressCallback) progressCallback(100);
        
        return { success: true, groupName, txtPath, mediaCount: mediaFiles.length };
    } catch (error) {
        console.error('Upload failed:', error);
        throw error;
    }
}

async function uploadFileToGitHub(file, path) {
    const content = await fileToBase64(file);
    const response = await fetch(
        `https://api.github.com/repos/${API_CONFIG.GITHUB_REPO}/contents/${path}`,
        {
            method: 'PUT',
            headers: {
                'Authorization': `token ${API_CONFIG.GITHUB_TOKEN}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: `Upload WhatsApp export: ${path}`,
                content: content.split(',')[1],
            }),
        }
    );
    if (!response.ok) throw new Error(`GitHub upload failed: ${response.statusText}`);
    return path;
}

async function triggerWhatsAppWorkflow(groupName, txtPath, mediaDir, fetchMetadata) {
    const response = await fetch(
        `https://api.github.com/repos/${API_CONFIG.GITHUB_REPO}/actions/workflows/whatsapp_processor.yml/dispatches`,
        {
            method: 'POST',
            headers: {
                'Authorization': `token ${API_CONFIG.GITHUB_TOKEN}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ref: 'main',
                inputs: {
                    group_name: groupName,
                    txt_file_path: txtPath,
                    media_dir_path: mediaDir,
                    fetch_link_metadata: fetchMetadata.toString(),
                },
            }),
        }
    );
    if (!response.ok) throw new Error(`Workflow trigger failed: ${response.statusText}`);
    return { success: true };
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

async function fetchGroups() {
    const response = await fetch(
        `${API_CONFIG.SUPABASE_URL}/rest/v1/whatsapp_groups?select=*&order=export_date.desc`,
        {
            headers: {
                'apikey': API_CONFIG.SUPABASE_ANON_KEY,
                'Authorization': `Bearer ${API_CONFIG.SUPABASE_ANON_KEY}`,
            },
        }
    );
    if (!response.ok) throw new Error('Failed to fetch groups');
    return response.json();
}

async function fetchMessages(groupId, limit = 100, offset = 0) {
    const response = await fetch(
        `${API_CONFIG.SUPABASE_URL}/rest/v1/whatsapp_messages?group_id=eq.${groupId}&select=*&order=message_timestamp.asc&limit=${limit}&offset=${offset}`,
        {
            headers: {
                'apikey': API_CONFIG.SUPABASE_ANON_KEY,
                'Authorization': `Bearer ${API_CONFIG.SUPABASE_ANON_KEY}`,
            },
        }
    );
    if (!response.ok) throw new Error('Failed to fetch messages');
    return response.json();
}

async function fetchLinks(groupId) {
    const response = await fetch(
        `${API_CONFIG.SUPABASE_URL}/rest/v1/whatsapp_links?group_id=eq.${groupId}&select=*&order=shared_at.desc`,
        {
            headers: {
                'apikey': API_CONFIG.SUPABASE_ANON_KEY,
                'Authorization': `Bearer ${API_CONFIG.SUPABASE_ANON_KEY}`,
            },
        }
    );
    if (!response.ok) throw new Error('Failed to fetch links');
    return response.json();
}

async function fetchMedia(groupId, fileType = null) {
    let url = `${API_CONFIG.SUPABASE_URL}/rest/v1/whatsapp_media?group_id=eq.${groupId}&select=*&order=uploaded_at.desc`;
    if (fileType) url += `&file_type=eq.${fileType}`;
    
    const response = await fetch(url, {
        headers: {
            'apikey': API_CONFIG.SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${API_CONFIG.SUPABASE_ANON_KEY}`,
        },
    });
    if (!response.ok) throw new Error('Failed to fetch media');
    return response.json();
}

function loadAPIConfig() {
    const storedToken = localStorage.getItem('github_token');
    const storedKey = localStorage.getItem('supabase_key');
    if (storedToken) API_CONFIG.GITHUB_TOKEN = storedToken;
    if (storedKey) API_CONFIG.SUPABASE_ANON_KEY = storedKey;
}

loadAPIConfig();

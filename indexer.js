const axios = require('axios');

const sendSMS = async () => {
    const apiKey = '546b953a95a4f0feba9b4a97ae8f91ca-1c512bb9-07ef-4d1c-a431-2d363ecc8c11';
    const baseUrl = 'https://ggv2z6.api.infobip.com';
    const path = '/sms/2/text/advanced';
    
    const postData = {
        "messages": [
            {
                "destinations": [{"to":"233552297798"}],
                "from": "ServiceSMS",
                "text": "Congratulations on sending your first message.\nGo ahead and check the delivery report in the next step."
            }
        ]
    };
    
    try {
        const response = await axios.post(
            `${baseUrl}${path}`,
            postData,
            {
                headers: {
                    'Authorization': `App ${apiKey}`,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            }
        );

        console.log(response.data);
    } catch (error) {
        console.error('Error sending message:', error.response ? error.response.data : error.message);
    }
};

// Example usage
sendSMS();

"use strict";

async function copyToClipboard(textToCopy) {
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(textToCopy);
    } else {
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        textArea.style.position = 'absolute';
        textArea.style.left = '-999999px';

        document.body.prepend(textArea);
        textArea.select();

        try {
            document.execCommand('copy');
        } catch (error) {
            console.error(error);
        } finally {
            textArea.remove();
        }
    }
}


function removeWithFadeOut(element) {
    element.classList.add('fade-out-down');
    element.addEventListener('animationend', () => element.remove());
}


function createElementFromHTML(html) {
    const wrapper = document.createElement('div');
    wrapper.innerHTML = html.trim();
    const element = wrapper.firstChild;
    wrapper.remove();
    return element;
}


function alertPopup(message) {
    const popup = document.createElement("div");
    popup.className = "alert-popup";
    const div2 = document.createElement("div");
    const text1 = document.createTextNode(`Error`);
    div2.appendChild(text1);
    const div3 = document.createElement("div");
    const text2 = document.createTextNode(`${message}`);
    div3.appendChild(text2);
    popup.appendChild(div2);
    popup.appendChild(div3);
    document.body.appendChild(popup);
    popup.addEventListener('animationend', () => popup.remove());
};


function createVideoMetadataElement({ thumbnail, title, channel, id }) {
    const element = document.createElement("div");
    element.className = "video-metadata fade-in-down";
    const img1 = document.createElement("img");
    img1.className = "meta-video-thumbnail";
    img1.alt = `The thumbnail of ${title}`;
    const p1 = document.createElement("p");
    p1.className = "meta-video-text-wrap";
    const span1 = document.createElement("span");
    span1.className = "meta-video-title";
    const span2 = document.createElement("span");
    span2.className = "meta-channel-name";
    p1.appendChild(span1);
    p1.appendChild(span2);
    element.appendChild(img1);
    element.appendChild(p1);
    element.querySelector('.meta-video-thumbnail').src = thumbnail;
    element.querySelector('.meta-video-title').innerText = title;
    element.querySelector('.meta-channel-name').innerText = channel;
    p1.innerHTML += ('<div class="share-btn-wrap"><svg class="share-btn" width="31px" height="31px" viewBox="0 -0.5 25 25" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M8.25005 8.5C8.25005 8.91421 8.58584 9.25 9.00005 9.25C9.41426 9.25 9.75005 8.91421 9.75005 8.5H8.25005ZM9.00005 8.267H9.75006L9.75004 8.26283L9.00005 8.267ZM9.93892 5.96432L10.4722 6.49171L9.93892 5.96432ZM12.2311 5V4.24999L12.2269 4.25001L12.2311 5ZM16.269 5L16.2732 4.25H16.269V5ZM18.5612 5.96432L18.0279 6.49171V6.49171L18.5612 5.96432ZM19.5 8.267L18.75 8.26283V8.267H19.5ZM19.5 12.233H18.75L18.7501 12.2372L19.5 12.233ZM18.5612 14.5357L18.0279 14.0083L18.5612 14.5357ZM16.269 15.5V16.25L16.2732 16.25L16.269 15.5ZM16 14.75C15.5858 14.75 15.25 15.0858 15.25 15.5C15.25 15.9142 15.5858 16.25 16 16.25V14.75ZM9.00005 9.25C9.41426 9.25 9.75005 8.91421 9.75005 8.5C9.75005 8.08579 9.41426 7.75 9.00005 7.75V9.25ZM8.73105 8.5V7.74999L8.72691 7.75001L8.73105 8.5ZM6.43892 9.46432L6.97218 9.99171L6.43892 9.46432ZM5.50005 11.767H6.25006L6.25004 11.7628L5.50005 11.767ZM5.50005 15.734L6.25005 15.7379V15.734H5.50005ZM8.73105 19L8.72691 19.75H8.73105V19ZM12.769 19V19.75L12.7732 19.75L12.769 19ZM15.0612 18.0357L14.5279 17.5083L15.0612 18.0357ZM16 15.733H15.25L15.2501 15.7372L16 15.733ZM16.75 15.5C16.75 15.0858 16.4143 14.75 16 14.75C15.5858 14.75 15.25 15.0858 15.25 15.5H16.75ZM9.00005 7.75C8.58584 7.75 8.25005 8.08579 8.25005 8.5C8.25005 8.91421 8.58584 9.25 9.00005 9.25V7.75ZM12.7691 8.5L12.7732 7.75H12.7691V8.5ZM15.0612 9.46432L15.5944 8.93694V8.93694L15.0612 9.46432ZM16.0001 11.767L15.2501 11.7628V11.767H16.0001ZM15.2501 15.5C15.2501 15.9142 15.5858 16.25 16.0001 16.25C16.4143 16.25 16.7501 15.9142 16.7501 15.5H15.2501ZM9.75005 8.5V8.267H8.25005V8.5H9.75005ZM9.75004 8.26283C9.74636 7.60005 10.0061 6.96296 10.4722 6.49171L9.40566 5.43694C8.65985 6.19106 8.24417 7.21056 8.25006 8.27117L9.75004 8.26283ZM10.4722 6.49171C10.9382 6.02046 11.5724 5.75365 12.2352 5.74999L12.2269 4.25001C11.1663 4.25587 10.1515 4.68282 9.40566 5.43694L10.4722 6.49171ZM12.2311 5.75H16.269V4.25H12.2311V5.75ZM16.2649 5.74999C16.9277 5.75365 17.5619 6.02046 18.0279 6.49171L19.0944 5.43694C18.3486 4.68282 17.3338 4.25587 16.2732 4.25001L16.2649 5.74999ZM18.0279 6.49171C18.494 6.96296 18.7537 7.60005 18.7501 8.26283L20.25 8.27117C20.2559 7.21056 19.8402 6.19106 19.0944 5.43694L18.0279 6.49171ZM18.75 8.267V12.233H20.25V8.267H18.75ZM18.7501 12.2372C18.7537 12.8999 18.494 13.537 18.0279 14.0083L19.0944 15.0631C19.8402 14.3089 20.2559 13.2894 20.25 12.2288L18.7501 12.2372ZM18.0279 14.0083C17.5619 14.4795 16.9277 14.7463 16.2649 14.75L16.2732 16.25C17.3338 16.2441 18.3486 15.8172 19.0944 15.0631L18.0279 14.0083ZM16.269 14.75H16V16.25H16.269V14.75ZM9.00005 7.75H8.73105V9.25H9.00005V7.75ZM8.72691 7.75001C7.6663 7.75587 6.65146 8.18282 5.90566 8.93694L6.97218 9.99171C7.43824 9.52046 8.07241 9.25365 8.73519 9.24999L8.72691 7.75001ZM5.90566 8.93694C5.15985 9.69106 4.74417 10.7106 4.75006 11.7712L6.25004 11.7628C6.24636 11.1001 6.50612 10.463 6.97218 9.99171L5.90566 8.93694ZM4.75005 11.767V15.734H6.25005V11.767H4.75005ZM4.75006 15.7301C4.73847 17.9382 6.51879 19.7378 8.72691 19.75L8.7352 18.25C7.35533 18.2424 6.2428 17.1178 6.25004 15.7379L4.75006 15.7301ZM8.73105 19.75H12.769V18.25H8.73105V19.75ZM12.7732 19.75C13.8338 19.7441 14.8486 19.3172 15.5944 18.5631L14.5279 17.5083C14.0619 17.9795 13.4277 18.2463 12.7649 18.25L12.7732 19.75ZM15.5944 18.5631C16.3402 17.8089 16.7559 16.7894 16.75 15.7288L15.2501 15.7372C15.2537 16.3999 14.994 17.037 14.5279 17.5083L15.5944 18.5631ZM16.75 15.733V15.5H15.25V15.733H16.75ZM9.00005 9.25H12.7691V7.75H9.00005V9.25ZM12.7649 9.24999C13.4277 9.25365 14.0619 9.52046 14.5279 9.99171L15.5944 8.93694C14.8486 8.18282 13.8338 7.75587 12.7732 7.75001L12.7649 9.24999ZM14.5279 9.99171C14.994 10.463 15.2537 11.1001 15.2501 11.7628L16.75 11.7712C16.7559 10.7106 16.3402 9.69106 15.5944 8.93694L14.5279 9.99171ZM15.2501 11.767V15.5H16.7501V11.767H15.2501Z" fill="#000000"></path> </g></svg> <svg class="share-btn-check" style="display:none" width="23px" height="23px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M4 12.6111L8.92308 17.5L20 6.5" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg></div>');
    p1.querySelector('.share-btn').onclick = event => {
        copyToClipboard(`${window.location.origin}?url=v=${id}`);
        const copyMessage = document.createElement('span')
        copyMessage.innerText = 'Link copied to clipboard';
        document.querySelector('.share-btn-check').style.display = 'block';
        event.target.style.display = 'none';
        event.target.parentElement.appendChild(copyMessage);
        setTimeout(() => {
            copyMessage.remove();
            document.querySelector('.share-btn-check').style.display = 'none';
            event.target.style.display = 'block';
        }, 2000)
    }

    return element;
}

function createFormatSelectElement(formats) {
    const element = document.createElement("div");
    element.className = "format-select fade-in-down";
    const div1 = document.createElement("div");
    div1.className = "format-select-type";
    const input1 = document.createElement("input");
    input1.id = `format-select-type-video`;
    input1.type = `radio`;
    input1.name = `type-select`;
    input1.checked = true;
    const label1 = document.createElement("label");
    label1.setAttribute("for", "format-select-type-video");
    const text1 = document.createTextNode(`Video`);
    label1.appendChild(text1);
    const input2 = document.createElement("input");
    input2.id = `format-select-type-audio`;
    input2.type = `radio`;
    input2.name = `type-select`;
    const label2 = document.createElement("label");
    label2.setAttribute("for", "format-select-type-audio");
    const text2 = document.createTextNode(`Audio`);
    label2.appendChild(text2);
    div1.appendChild(input1);
    div1.appendChild(label1);
    div1.appendChild(input2);
    div1.appendChild(label2);
    const div2 = document.createElement("div");
    div2.className = "format-select-quality";
    const select1 = document.createElement("select");
    select1.className = "format-select-quality-video";
    const select2 = document.createElement("select");
    select2.className = "format-select-quality-audio";
    select2.style = `display: none;`;
    div2.appendChild(select1);
    div2.appendChild(select2);
    element.appendChild(div1);
    element.appendChild(div2);

    Object.entries(formats).forEach(([type, options]) => {
        const selectElement = element.querySelector(`.format-select-quality-${type}`);
        options.forEach(([mimeType, quality, ids]) => {
            const option = document.createElement('option');
            option.value = ids.join('|');
            let type = mimeType.split('/')[0];
            let format = mimeType.split('/')[1];
            if (type == 'audio' && format == 'mp4') {
                format = 'm4a';
            }
            option.innerText = `${format} - ${quality}${ids.length === 1 && !ids[0].endsWith('cvt') ? ' (Fast)' : ''}`;
            selectElement.appendChild(option);
        });
    });

    element.querySelector('#format-select-type-video').addEventListener('input', () => {
        toggleQualitySelect(element, 'video');
        document.querySelector('.download-name-format-ext').innerText = getSelectedFormatExtention();
    });

    element.querySelector('#format-select-type-audio').addEventListener('input', () => {
        toggleQualitySelect(element, 'audio');
        document.querySelector('.download-name-format-ext').innerText = getSelectedFormatExtention();
    });

    element.querySelectorAll('select').forEach(e => {
        e.addEventListener('input', () => {
            document.querySelector('.download-name-format-ext').innerText = getSelectedFormatExtention();
        });
    });

    return element;
}


function getSelectedFormatExtention() {
    const selected = getSelectedFormat();
    const type = selected[0];
    const format = selected[1].options[selected[1].selectedIndex].innerText.split(' ')[0];
    let ext;
    if (type == 'video') {
        ext = 'mp4';
    }
    if (type == 'audio') {
        if (format == 'mp4') {
            ext = 'm4a';
        } else {
            ext = format;
        }
    }
    return ext;
}


function createDownloadNameFormatForm() {
    const downloadNameFormat = window.localStorage['dnf'] || '[title]';
    const extention = getSelectedFormatExtention();
    const element = document.createElement("div");
    element.className = "download-name-format-form fade-in-down";
    const div2 = document.createElement("div");
    div2.className = "option-label";
    const label1 = document.createElement("label");
    label1.setAttribute("for", "download-name-format-input");
    const text1 = document.createTextNode(`File Name`);
    label1.appendChild(text1);
    div2.appendChild(label1);
    const div3 = document.createElement("div");
    const input1 = document.createElement("input");
    input1.id = `download-name-format-input`;
    input1.value = `${downloadNameFormat}`;
    const text2 = document.createTextNode(`.`);
    const span1 = document.createElement("span");
    span1.className = "download-name-format-ext";
    const text3 = document.createTextNode(`${extention}`);
    span1.appendChild(text3);
    div3.appendChild(input1);
    div3.appendChild(text2);
    div3.appendChild(span1);
    const div4 = document.createElement("div");
    const text4 = document.createTextNode(`*[title]=video title, [channel]=channel name, [id]=video id`);
    div4.appendChild(text4);
    element.appendChild(div2);
    element.appendChild(div3);
    element.appendChild(div4);
    return element;
}


function toggleQualitySelect(element, type) {
    element.querySelector('.format-select-quality-video').style.display = type === 'video' ? 'block' : 'none';
    element.querySelector('.format-select-quality-audio').style.display = type === 'audio' ? 'block' : 'none';
}


function createRangeSelectForm(rangeEnd) {
    const div1 = document.createElement("div");
    div1.className = "range-select-form fade-in-down";
    const div2 = document.createElement("div");
    div2.className = "option-label";
    const label1 = document.createElement("label");
    const text1 = document.createTextNode(`Range`);
    label1.appendChild(text1);
    div2.appendChild(label1);
    const div3 = document.createElement("div");
    const input1 = document.createElement("input");
    input1.className = "range-start";
    input1.setAttribute("placeholder", `00:00:00`);
    const text2 = document.createTextNode(`~`);
    const input2 = document.createElement("input");
    input2.className = "range-end";
    input2.setAttribute("placeholder", `${rangeEnd}`);
    div3.appendChild(input1);
    div3.appendChild(text2);
    div3.appendChild(input2);
    div1.appendChild(div2);
    div1.appendChild(div3);
    return div1;
}


function createDownloadButton() {
    const button = createElementFromHTML('<button class="next-2-btn fade-in-down">Download</button>');
    button.addEventListener('click', async () => {
        const rangeStart = document.querySelector('.range-start').value || '';
        const rangeEnd = document.querySelector('.range-end').value || '';

        const format = getSelectedFormat()[1].value;
        const downloadNameFormat = document.querySelector('#download-name-format-input').value;
        localStorage['dnf'] = downloadNameFormat;
        removeWithFadeOut(button);
        removeWithFadeOut(document.querySelector('.format-select'));
        removeWithFadeOut(document.querySelector('.download-name-format-form'));
        removeWithFadeOut(document.querySelector('.range-select-form'));
        const statusWindow = createElementFromHTML('<div class="status-window"></div>');
        document.querySelector('.step-1-wrap').appendChild(statusWindow);

        const response = await fetch('./download/s', {
            method: 'POST',
            body: JSON.stringify({
                format: format,
                start: rangeStart,
                end: rangeEnd
            }),
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            alertPopup((await response.json()).error || 'An error occured');
            return;
        }
        await processDownload(downloadNameFormat);
    });
    return button;
}


function getSelectedFormat() {
    const selectedType = document.querySelector('.format-select-type input:checked').id.split('-').pop();
    const selectElement = document.querySelector(`.format-select-quality-${selectedType}`);
    return [selectedType, selectElement];
}


function getInputURL() {
    return document.querySelector('.vidurl-input').value;
}


async function getSearch(query) {
    const response = await fetch('./search', {
        method: 'POST',
        body: JSON.stringify({
            query: query
        }),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
}


async function downloadInit(url) {
    return await fetch(`./download/init?url=${encodeURIComponent(url)}`);
}


function createSearchResultElement(metadata) {
    const videoId = metadata.id;
    const title = metadata.title;
    const channel = metadata.channel;
    const thumbnail = `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`;
    const elem = document.createElement("div");
    elem.className = "search-item";
    const img1 = document.createElement("img");
    img1.setAttribute("src", `${thumbnail}`);
    img1.setAttribute("alt", `The thumbnail of ${videoId}`);
    const div1 = document.createElement("div");
    div1.className = "meta-video-text-wrap";
    const span1 = document.createElement("span");
    span1.className = "meta-video-title search-item-title";
    const text1 = document.createTextNode(`${title}`);
    span1.appendChild(text1);
    const span2 = document.createElement("span");
    span2.className = "meta-channel-name";
    const text2 = document.createTextNode(`${channel}`);
    span2.appendChild(text2);
    div1.appendChild(span1);
    div1.appendChild(span2);
    elem.appendChild(img1);
    elem.appendChild(div1);
    elem.addEventListener('click', event => {
        document.querySelector('.vidurl-input').value = `v=${videoId}`;
        document.querySelector('.next-1-btn').click();
    });
    return elem;
}


async function searchVideos(query) {
    const searchResults = await getSearch(query);
    const step1Wrap = document.querySelector('.step-1-wrap');
    const searchItemsWrap = document.createElement('div');
    searchItemsWrap.classList.add('search-items-wrap');
    searchItemsWrap.classList.add('fade-in-down');
    searchResults.forEach(e => {
        searchItemsWrap.appendChild(createSearchResultElement(e));
    });
    step1Wrap.appendChild(searchItemsWrap);
}


document.querySelector('.next-1-btn').addEventListener('click', async event => {
    const step1Wrap = document.querySelector('.step-1-wrap');
    step1Wrap.innerHTML = '';
    event.target.disabled = true;
    const loader = createElementFromHTML('<span class="loader"></span>');
    step1Wrap.appendChild(loader);

    const url = getInputURL();
    if (!url.match(/(?:v=|\/)([0-9A-Za-z_-]{11})/)) {
        await searchVideos(url);
        loader.remove();
        event.target.disabled = false;
        return;
    }

    try {
        const response = await downloadInit(url);
        if (!response.ok) throw '';
        loader.remove();
        const videoMetadata = await response.json();
        step1Wrap.appendChild(createVideoMetadataElement(videoMetadata));
        step1Wrap.appendChild(createFormatSelectElement(videoMetadata.formats));
        step1Wrap.appendChild(createDownloadNameFormatForm());
        step1Wrap.appendChild(createRangeSelectForm(videoMetadata.range))
        step1Wrap.appendChild(createDownloadButton());
    } catch (error) {
        step1Wrap.innerHTML = '';
        loader.remove();
        alertPopup('Could not retrieve video information.');
    } finally {
        event.target.disabled = false;
    }
});


async function processDownload(downloadNameFormat) {
    sse = new EventSource('./download/status');
    sse.onmessage = event => {
        const statusWindow = document.querySelector('.status-window');
        const status = JSON.parse(event.data);

        if (status.step == 1) {
            statusWindow.innerHTML = `Downloading Video... <progress max="1" value="${status.progress}"></progress> ${Math.round(status.progress * 100)}%`;
        }

        if (status.step == 2) {
            statusWindow.innerHTML = `Downloading Audio... <progress max="1" value="${status.progress}"></progress> ${Math.round(status.progress * 100)}%`;
        }

        if (status.step == 3) {
            statusWindow.innerHTML = `Merging video and audio... <progress max="1" value="${status.progress}"></progress> ${Math.round(status.progress * 100)}%`;
        }

        if (status.step == 4) {
            statusWindow.innerHTML = `Converting file... <progress max="1" value="${status.progress}"></progress> ${Math.round(status.progress * 100)}%`;
        }

        if (status.step == 5) {
            statusWindow.innerHTML = `Cutting file... <progress max="1" value="${status.progress}"></progress> ${Math.round(status.progress * 100)}%`;
        }

        if (status.step == 8) {
            statusWindow.innerHTML = '<strong><span style="color:red">Failed to download the video, please try again.</span></strong>';
            sse.close();
        }

        if (status.step == 9) {
            statusWindow.innerHTML = '<strong>Download completed!</strong>';
            const fileId = status.fileId;
            var hiddenElement = document.createElement('a');
            hiddenElement.href = `./download?file=${fileId}&dnf=${encodeURIComponent(downloadNameFormat)}`;
            hiddenElement.click();
            sse.close()
        }
    }
}


document.querySelector('.vidurl-input').addEventListener('keypress', event => {
    if (event.key === 'Enter') {
        event.preventDefault();
        document.querySelector('.next-1-btn').click();
    }
});


window.addEventListener('DOMContentLoaded', event => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const url = urlParams.get('url')
    if (url) {
        document.querySelector('.vidurl-input').value = url;
        document.querySelector('.next-1-btn').click();
    }
})

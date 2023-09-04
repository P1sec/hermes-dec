function format_size(size) { // Format a size in MiB or KiB
    if(size >= 1024 * 1024) { // More than 1 MiB?
        return Math.floor(size / 1024 / 1024 * 10) / 10 + ' MiB';
    }
    else {
        return Math.floor(size / 1024 / 1024 * 10) / 10 + ' KiB';
    }
};

function format_date(date) {
    return date; // WIP
};

function to_hex(buf) { // buffer is an ArrayBuffer
    return [...new Uint8Array(buf)]
        .map(x => x.toString(16).padStart(2, '0'))
        .join('');
};
  

async function hash_file_buffer(file_buffer) {
    return to_hex(
        await window.crypto.subtle.digest('SHA-256', file_buffer)
    );
};


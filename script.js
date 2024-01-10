// // Based on https://github.com/LinusU/base32-encode/blob/master/index.js
// function hex_to_b32(hex) {
//     let alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
//     let bytes = [];
//     for (let i = 0; i < hex.length; i += 2) {
//         bytes.push(parseInt(hex.substr(i, 2), 16));
//     }
//     let bits = 0;
//     let value = 0;
//     let output = '';
//     for (let i = 0; i < bytes.length; i++) {
//         value = (value << 8) | bytes[i];
//         bits += 8;
//         while (bits >= 5) {
//             output += alphabet[(value >>> (bits - 5)) & 31];
//             bits -= 5;
//         }
//     }
//     if (bits > 0) {
//         output += alphabet[(value << (5 - bits)) & 31];
//     }
//     return output;
// }

// function dump_secrets() {
//     const secrets = [];

//     appManager.getModel().map(function (i) {
//         var secretSeed = i.secretSeed;
//         if (typeof secretSeed == 'undefined') {
//             secretSeed = i.encryptedSeed;
//         }
//         var secret = i.markedForDeletion === false ? i.decryptedSeed : hex_to_b32(secretSeed);
//         var period = i.digits === 7 ? 10 : 30;
//         // var totp_uri = `otpauth://totp/${encodeURIComponent(i.name)}?secret=${secret}&digits=${
//         //     i.digits
//         // }&period=${period}`;

//         secrets.push({ name: i.name, secret });
//     });

//     return JSON.stringify(secrets);
// }

// dump_secrets();

function hex_to_b32(e){let t='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',r=[];for(let n=0;n<e.length;n+=2)r.push(parseInt(e.substr(n,2),16));let d=0,o=0,s='';for(let u=0;u<r.length;u++)for(o=o<<8|r[u],d+=8;d>=5;)s+=t[o>>>d-5&31],d-=5;return d>0&&(s+=t[o<<5-d&31]),s}function dump_secrets(){let e=[];return appManager.getModel().map(function(t){var r=t.secretSeed;void 0===r&&(r=t.encryptedSeed);var n=!1===t.markedForDeletion?t.decryptedSeed:hex_to_b32(r);t.digits,e.push({name:t.name,secret:n})}),JSON.stringify(e)}dump_secrets();
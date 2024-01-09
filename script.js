// Based on https://github.com/LinusU/base32-encode/blob/master/index.js
function hex_to_b32(hex) { let alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"; let bytes = []; for (let i = 0; i < hex.length; i += 2) { bytes.push(parseInt(hex.substr(i, 2), 16)); } let bits = 0; let value = 0; let output = ''; for (let i = 0; i < bytes.length; i++) { value = (value << 8) | bytes[i]; bits += 8; while (bits >= 5) { output += alphabet[(value >>> (bits - 5)) & 31]; bits -= 5; } } if (bits > 0) { output += alphabet[(value << (5 - bits)) & 31]; } return output; }

console.clear();
console.warn("Here's your Authy tokens:");
var data = appManager.getModel().map(function(i) {
var secretSeed = i.secretSeed;
if (typeof secretSeed == 'undefined') {
   secretSeed = i.encryptedSeed;
}
var secret = (i.markedForDeletion === false ? i.decryptedSeed : hex_to_b32(secretSeed));
var period = (i.digits === 7 ? 10 : 30);
var totp_uri = `otpauth://totp/${encodeURIComponent(i.name)}?secret=${secret}&digits=${i.digits}&period=${period}`;
console.group(`${i.originalName} / ${i.name}`);
  console.log('TOTP secret:', secret);
  console.log('TOTP URI:', totp_uri);
console.groupEnd();
return {name: i.name, secret: secret};
});
//console.save(data, 'authy_backup.json');
# 1 Beginnings of Cryptography

Cryptography or the art of concealing meaning in writing ist over 4000 years old. 

# 2 Various Chiffres

# 3 The computational Revolution

The advent of the electronic computer changed the field of cryptography fundamentally. Starting with the "bombe", produced by Alan Turing and refined by Gordon Welchman around 1940, the world ushered into a new era of automated de- and encryption. 
The bombe is an electro-mechanical device that was key to breaking the ciphers produced by the enigma - a device used by the german military in the second world war to secure their communications. Turings bombe was the first machine that was able to break message encryption in an automated fashion. Previously cryptoanalysts had to break ciphers "by hand" i.e. by doing manual frequency analysis for example. Breaking the enemies communication provided a vital advantage for the Allies during World War Two.
The next cryptographic revolution came in 1971 when Whitfield Diffie invented public-key-cryptography, single-handedly eliminating a problem that haunted cryptographers from the beginnigs of their field of expertise: the establishing of a shared secret over insecure channels, also known as the key distribution problem. Previously the security of an encryption scheme based on the fact, that there was atleast one element in said scheme, that must remain unknown to malicious parties intending to attack and decipher the communication, for example a password. Public-key-cryptography does not work like this: Parties wishing to communicate simply exchange their public keys over an unsecured channel and are able to establish a guaranteed shared secret from that. Without knowing the corresponding private keys, the public keys are worthless in the eyes of an attacker. But the maths behind Public-key-cryptography is prohibitively expensive if one attemts to encrypt something this way by hand. Progress like this was only possible by utilising electronic computers.
When those computers later on became widely available for a broader range of people, suddenly everyone was able to encrypt information with complicated schemes. And for the first time the security of those schemes was mathematically provable. In fact the prove of some of those later schemes guaranteed protection even from entities with massive resources, manpower and expertise without the need for skilled and qualified cryptographers. 
The first openly available standart for electronic encryption was a symmetric cipher called "Data Encryption Standard" or DES. Developed in the early 1970s at IBM the cipher was published in 1977 as an official Federeal Information Processing Standard (FIPS). The security of DES was disputed right from its first publication. Even in the late seventies the key length was critisized as too short, although it took until June of 1997 before the first DES message was publicly decrypted via brute force attack. In January of the same year the search for a predecessor of DES was announced by the National Institute of Standards and Technology of the United States (NIST). This predecessor supposed to be "an unclassified, publicly disclosed encryption algorithm capable of protecting sensitive government information well into the next century." To increase trust into this standard-to-be the search was public and NIST relied on submissions from the cryptographic community. 

# 4 The Advanced Encryption Standart selection

The formal call for submissions of AES canidates came in september of 1997. NIST explicitly requested input from outside of the institution by explicitly asking "the public, academic/research communities, manufacturers, voluntary standards organizations, and Federal, state, and local government organizations." The submissions would be made public for review and comment after the submission period came to an end.

## 4.1 AES: requirements

The proposed algorithms for the new encrytion standard and thus the potential successors of DES had to fullfill a number of requirements in order for them to be concidered by NIST.
AES was intended to be a block cipher operating on 128 bits at a time. Those bits should be secured by key length of atleast the three sizes 128, 192 and 256 bits. 
The canidates would be furthermore analyzed and evaluated regarding:

* *security*: Deemed as the most important criterion, it encompasses factors like the actual security compared to the competitors, the degree to which the algorithm is able to produce an output indistinguishable to a random permutation of the input, the quality of the mathematical prinicples behind the algorithm and of course critique, concerns and attacks regarding the canidate originating from the public review.
* *cost*: Financial cost was one concideration: All canidates had to be released on a "worldwide, non-exclusive, royalty-free basis." before they could be submitted. Performance costs like the speed of the algorithm both in software and hardware implementations or memory size, be it in code size, gate count for hardware implementations or RAM requirements for software implementations were further factors that played a role in this category.
* *algorithm and implementation characteristics*:Flexibility without compromising security was another desirable aspect of the new standard. Additonal key sizes to those specified in the minimum requirements, the possibility of implementation on a variety of platforms, from slower 8-bit SmartCard processors to fully-fledged desktop CPUs and other fields of applications like usage as a stream cipher, message authentication generator, pseudorandom number generator, hashing algorithm and more were all attributes to the flexibility of an encryption algorithm an thus factors, that influenced the AES-comittee in their final decision. The last aspect under which the standard-to-be had to prove itself was simplicity, where a simpler algorithm, that holds up well under all other aspects, is preferable.

## 4.2 AES selection process

Nearly a year after requesting submissions, NIST published a list with fifteen canidates they deemed worthy of further investigation at the First AES Canidate Conference (AES1) in August 1998. The cryptographic community was invited to critique those choices, either via email or on the online discussion forum NIST hosted for this exact purpose. This input from the community was discussed at the Second AES Canidate Conference (AES2) in spring of 1999. Shortly after that NIST selected five finalists from the initial fifteen algorithms: MARS, RC6, Rijndael, Serpent, and Twofish.
The other canidates were excluded, partially because "serious questions \[had\] been raised about \[their\] security", partially because they were slower/potentially less secure than other comparable canidates.
The finalists moved on to recieve further scrutiny from both the NIST and the cryptographic community.

# 5 AES in review
## 5.1 NIST
## 5.2 Other Voices




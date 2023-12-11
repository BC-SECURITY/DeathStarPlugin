# DeathStar
<p align="center">
  <img src="https://user-images.githubusercontent.com/5151193/88892241-ddc6d700-d21a-11ea-9c37-3cffed86e2f8.png" alt="DeathStar" height="300"/>
</p>

Deathstar is an [Empire](https://github.com/BC-SECURITY/Empire) plugin that automates gaining Domain and/or Enterprise Admin rights in Active Directory environments using common offensive tactics, techniques, and procedures (TTPs).

## Motivation

The primary motivation behind the creation of this was to demonstrate how a lot of the commonly exploited Active Directory misconfiguration can be chained together to gain Administrator-level privileges in an automated fashion (akin to a worm).

While many more things could be taken advantage of (including server-side vulnerabilities such as MS17-010), DeathStar mainly focuses on exploiting misconfigurations/vulnerabilities that have a very low probability of causing any system/network stability issues.

Additionally, it now supports Active Directory environments with multiple Forests/Domains. It has an "Active Monitoring" feature, which allows it to adapt its attack path based on real-time changes in the network.

## Screenshots
<img width="511" alt="image" src="https://github.com/BC-SECURITY/DeathStarPlugin/assets/20302208/d3b258ec-d3d9-468f-b826-87fc5c34f97f">
<img width="788" alt="image" src="https://github.com/BC-SECURITY/DeathStarPlugin/assets/20302208/322a8b2c-7e25-4d51-b1b6-410a8d39b37b">

## Acknowledgments
This project is built upon [DeathStar by byt3bl33d3r](https://github.com/byt3bl33d3r/DeathStar)

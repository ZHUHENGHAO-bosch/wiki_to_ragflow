# Aurix Safety - Board Bringup dependencies

> Source: /spaces/CARSFW/pages/3057794119/Aurix+Safety+-+Board+Bringup+dependencies
> Last modified: 2023-05-22T09:21:30.000+02:00

---

### Introduction

There are certain features in Safety which has to be configured in case of new board bring up activity.

#### Safety Mechanisms to be considered for board bring up

Preconditions:

SM10 Safe Config shall provide the board ID to all Safe modules

1. RegM
2. WDG

Better not to change the WDG pin in different samples

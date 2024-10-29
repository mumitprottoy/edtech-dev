const countDown = (secsLeft, unitNames, functions) => {
    const secs = 60; 
    const mod = (a, b) => ((a % b) + b) % b;

    const setClock = () => {
        let _clock = Array(unitNames.length).fill(0);
        const setUnit = (_secsLeft, n = _clock.length - 1) => {
            if (n >= 0) {
                const _secs = secs ** n;
                _clock[Math.abs(
                    n - _clock.length + 1)] = Math.floor(_secsLeft / _secs);
                return setUnit(_secsLeft % _secs, n = n - 1);
            }
            return null;
        }
        setUnit(secsLeft); return _clock;
    }

    let clock = setClock();
    
    const printClock = () => {
        for (let i = 0; i < clock.length; i += 1) {
            let unit = clock[i].toString();
            if (unit.length == 1) unit = '0' + unit;
            document.getElementById(unitNames[i]).innerText = unit;
        }
    }

    const tick = (n = clock.length - 1) => {
        clock[n] = mod(clock[n] - 1, secs);
        if (clock[n] == secs - 1 && n >= 1)
            return tick(n = n - 1);
        return clock;
    }

    const runCountDown = () => {
        printClock();
        if (clock.reduce(
            (_, __) => _ + __, 0) == 0) {
                functions.forEach(f => f());
                clearInterval(countDownIntervalID);
            }
        tick();
    }

    let countDownIntervalID = setInterval(runCountDown, 1000);
}

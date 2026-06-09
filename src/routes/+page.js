const now = new Date()

const getLondonISOString = (dateObj) => {
    const formatter = new Intl.DateTimeFormat('sv-SE', {
        timeZone: 'Europe/London',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    });

    const formatted = formatter.format(dateObj);

    return formatted.replace(' ', 'T');
}

const yesterday = new Date(now.getTime() - 24*60*60*1000);

const todayURI = encodeURIComponent(getLondonISOString(now));
const yesterdayURI = encodeURIComponent(getLondonISOString(yesterday));

export const load = async({ fetch }) => {
    const priceRes = await fetch(`https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/market-index?from=${yesterdayURI}Z&to=${todayURI}Z&dataProviders=APXMIDP`)
    const priceData = await priceRes.json()
    const price = priceData.data

    return {
        price: price,
        now: now.toTimeString().substring(0,5)
    }
}
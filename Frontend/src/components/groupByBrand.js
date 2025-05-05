const groupByBrand = (phones) => {
    return phones.reduce((acc, phone) => {
        if (!acc[phone.brand]) {
            acc[phone.brand] = [];
        }
        acc[phone.brand].push(phone);
        return acc;
    }, {});
  };

  export default groupByBrand
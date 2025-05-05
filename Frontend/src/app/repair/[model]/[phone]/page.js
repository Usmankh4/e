"use client";
import { useParams, useRouter } from 'next/navigation';
import axios from 'axios';
import { useEffect, useState } from 'react';
import Header from '@/components/header';
import Footer from '@/components/footer';

export default function PhoneRepairServices() {
    const router = useRouter();
    const { phone } = useParams();
    const [repairServices, setRepairServices] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (phone) {
            const fetchRepairServices = async () => {
                setLoading(true);
                try {
                    
                    const res = await axios.get(`http://localhost:8000/myapp/api/phone-models/`);
                    setRepairServices(res.data.results);
                    console.log(res.data.results);
                } catch (error) {
                    console.error('Error fetching repair services:', error);
                } finally {
                    setLoading(false);
                }
            };
            fetchRepairServices();
        }
    }, [phone]);

    const phoneModel = repairServices.find(model => decodeURIComponent(phone) === model.name);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <Header />
            <div className="pageAfterHeader">
                <div className="RepairHeader">
                    <h2>{decodeURIComponent(phone)}</h2>
                    <div className='repairImage'></div>
                    <div className="RepairWrapper">
                       
                    {phoneModel && phoneModel.repair_services.length > 0 ? (
    <ul className="repairServicesList">
        {phoneModel.repair_services.map((service) => (
            <li key={service.id} className="repairServiceItem">
                <span className="serviceName">{service.service_type}</span>
                <span className="servicePrice">
                    {service.price === 'Free' ? service.price : `$${service.price}`}
                </span>
            </li>
        ))}
    </ul>
) : (
    <p>No repair services available for this model.</p>
)}


                    </div>
                </div>
            </div>
            <Footer />
        </div>
    );
}

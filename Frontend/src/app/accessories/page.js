import Layout from "../../components/Layout";
import AccessoryCard from "../../components/AccessoryCard";
import '../globals.css';

// Function to fetch accessories data server-side
async function getAccessories() {
  try {
    const response = await fetch('http://127.0.0.1:8000/myapp/api/accessories/', { 
      cache: 'no-store'
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch accessories: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching accessories:', error);
    return [];
  }
}

// Server Component
export default async function AccessoriesPage() {
  const accessories = await getAccessories();
  
  // Using the AccessoryCard component which exactly matches the ProductCard structure

  return (
    <Layout>
      <div className="PhoneTitle">
        <h2>ACCESSORIES</h2>
        
        {accessories && accessories.length > 0 ? (
          <>
            <div className="PhoneWrapper">
              <div className="PhoneLayout">
                {accessories.map((accessory) => (
                  <AccessoryCard 
                    key={accessory.id} 
                    accessory={accessory}
                  />
                ))}
              </div>
            </div>
          </>
        ) : (
          <div className="error">
            <p>No accessories found. Please check back later.</p>
          </div>
        )}
      </div>
    </Layout>
  );
}

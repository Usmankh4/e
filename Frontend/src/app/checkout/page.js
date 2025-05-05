import Footer from "../../components/footer";
import Header from "../../components/header";
import CartItems from "./CartItems";

export default function CheckoutPage() {
  return (
    <div className="page-container">
      <div className="content-wrap">
        <Header />
        <div className="pageAfterHeader">
          <CartItems />
        </div>
      </div>
      <Footer />
    </div>
  );
}

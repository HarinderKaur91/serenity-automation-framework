package starter.pageobjects.saucedemo;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class InventoryPageTest {

    @Test
    void shouldBuildAddToCartButtonIdForMultiWordProductName() {
        assertThat(InventoryPage.toAddToCartButtonId("Sauce Labs Backpack"))
                .isEqualTo("add-to-cart-sauce-labs-backpack");
    }

    @Test
    void shouldNormalizePunctuationWhenBuildingAddToCartButtonId() {
        assertThat(InventoryPage.toAddToCartButtonId("Sauce Labs Bolt T-Shirt"))
                .isEqualTo("add-to-cart-sauce-labs-bolt-t-shirt");
    }
}

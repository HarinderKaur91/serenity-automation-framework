package starter.pageobjects.saucedemo;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class InventoryPageTest {

    @Test
    void shouldBuildAddToCartButtonIdFromProductName() {
        assertThat(InventoryPage.addToCartButtonIdFor("Sauce Labs Backpack"))
                .isEqualTo("add-to-cart-sauce-labs-backpack");
    }

    @Test
    void shouldNormalizePunctuationAndWhitespaceWhenBuildingAddToCartButtonId() {
        assertThat(InventoryPage.addToCartButtonIdFor("  Sauce Labs Bolt T-Shirt  "))
                .isEqualTo("add-to-cart-sauce-labs-bolt-t-shirt");
    }
}

package starter.pageobjects.saucedemo;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class InventoryPageTest {

    @Test
    void shouldBuildTheExpectedSauceDemoSlugForMultiWordProducts() {
        assertThat(InventoryPage.toProductSlug("Sauce Labs Backpack"))
                .isEqualTo("sauce-labs-backpack");
    }

    @Test
    void shouldNormalizePunctuationInSauceDemoProductSlugs() {
        assertThat(InventoryPage.toProductSlug("Sauce Labs Bolt T-Shirt"))
                .isEqualTo("sauce-labs-bolt-t-shirt");
    }
}

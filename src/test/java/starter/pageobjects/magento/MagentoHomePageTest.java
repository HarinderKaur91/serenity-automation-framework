package starter.pageobjects.magento;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class MagentoHomePageTest {

    @Test
    void shouldDetectCloudflareSslErrorFromTitle() {
        assertThat(MagentoHomePage.isCloudflareSslErrorPage(
                "softwaretestingboard.com | 526: Invalid SSL certificate",
                ""))
                .isTrue();
    }

    @Test
    void shouldDetectOtherCloudflareErrorCodesFromTitle() {
        assertThat(MagentoHomePage.isCloudflareSslErrorPage(
                "softwaretestingboard.com | 525: SSL Handshake Failed",
                "")).isTrue();
        assertThat(MagentoHomePage.isCloudflareSslErrorPage(
                "softwaretestingboard.com | 522: Connection timed out",
                "")).isTrue();
        assertThat(MagentoHomePage.isCloudflareSslErrorPage(
                "softwaretestingboard.com | 521: Web server is down",
                "")).isTrue();
    }

    @Test
    void shouldDetectCloudflareSslErrorFromPageSourceMarkers() {
        String pageSource = """
                <html>
                <div id="cf-error-details">Invalid SSL certificate Error code 526</div>
                </html>
                """;

        assertThat(MagentoHomePage.isCloudflareSslErrorPage("", pageSource)).isTrue();
    }

    @Test
    void shouldDetectOtherCloudflareErrorsFromPageSource() {
        String pageSource = """
                <html>
                <div id="cf-error-details">Error code 522 Connection timed out</div>
                </html>
                """;

        assertThat(MagentoHomePage.isCloudflareSslErrorPage("", pageSource)).isTrue();
    }

    @Test
    void shouldNotTreatNormalSearchResultsAsCloudflareError() {
        String pageSource = """
                <html>
                <h1 class="page-title">Search results for: 'jacket'</h1>
                <strong class="product name product-item-name"><a class="product-item-link">Hero Hoodie</a></strong>
                </html>
                """;

        assertThat(MagentoHomePage.isCloudflareSslErrorPage("Search results for: 'jacket'", pageSource)).isFalse();
    }
}


import React from 'react';

interface SocialLink {
  name: string;
  href: string;
  icon: string;
}

const socialLinks: SocialLink[] = [
  { name: 'GitHub', href: '#', icon: '💻' },
  { name: 'LinkedIn', href: '#', icon: '💼' },
  { name: 'Twitter', href: '#', icon: '🐦' },
  { name: 'Email', href: '#', icon: '📧' },
];

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="relative z-10 border-t border-slate-800 mt-20 bg-slate-900/50 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-8 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center font-bold text-white shadow-lg">
                AH
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Algarve Hack
              </span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">
              Transformando ideias em realidade através da tecnologia e inovação no coração do Algarve.
            </p>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-white font-semibold text-lg">Links Rápidos</h3>
            <ul className="space-y-2">
              {['Sobre Nós', 'Projetos', 'Serviços', 'Blog', 'Contacto'].map((link) => (
                <li key={link}>
                  <a
                    href="#"
                    className="text-slate-400 hover:text-blue-400 transition-colors duration-300 text-sm"
                  >
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Info */}
          <div className="space-y-4">
            <h3 className="text-white font-semibold text-lg">Contacte-nos</h3>
            <div className="space-y-2 text-sm text-slate-400">
              <p>📍 Algarve, Portugal</p>
              <p>📧 info@algarvehack.pt</p>
              <p>📱 +351 XXX XXX XXX</p>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-slate-800 my-8" />

        {/* Bottom Footer */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="text-slate-400 text-center md:text-left">
            <p className="text-sm">
              © {currentYear} Algarve Hack. Todos os direitos reservados.
            </p>
            <p className="text-xs mt-1 text-slate-500">
              Feito com ❤️ no Algarve
            </p>
          </div>

          {/* Social Links */}
          <div className="flex gap-4">
            {socialLinks.map((social) => (
              <a
                key={social.name}
                href={social.href}
                className="w-10 h-10 bg-slate-800 hover:bg-slate-700 rounded-lg flex items-center justify-center transition-all duration-300 hover:scale-110 hover:shadow-lg hover:shadow-blue-500/30"
                aria-label={social.name}
                title={social.name}
              >
                <span className="text-lg">{social.icon}</span>
              </a>
            ))}
          </div>
        </div>

        {/* Legal Links */}
        <div className="flex justify-center gap-6 mt-6 text-xs text-slate-500">
          <a href="#" className="hover:text-slate-400 transition-colors">
            Política de Privacidade
          </a>
          <span>•</span>
          <a href="#" className="hover:text-slate-400 transition-colors">
            Termos de Serviço
          </a>
          <span>•</span>
          <a href="#" className="hover:text-slate-400 transition-colors">
            Cookies
          </a>
        </div>
      </div>
    </footer>
  );
};

